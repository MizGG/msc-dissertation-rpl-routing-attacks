#!/usr/bin/env python3
"""Local adversarial-profile DQN/DDQN IDS experiment over validated Cooja data.

No API, external service or runtime network is used. The adversary selects a
complete saved Cooja Sinkhole or Sybil profile; it cannot fabricate or alter
traffic. The defender is trained only on the first three target seeds and is
evaluated only on the final two target seeds.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, deque
from pathlib import Path

import torch
from torch import nn

from run_local_incremental_ids import DDM, OnlineGaussianNB


TRAIN_SEEDS = ("123456", "234567", "345678")
TEST_SEEDS = ("456789", "567890")
ACTION_NAMES = ("keep_source_model", "learn_delayed_label", "rebuild_from_target_history")
STATE_SIZE = 6
ACTION_COUNT = len(ACTION_NAMES)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def feature_state(row: dict[str, str], last_error: float, ddm_alarm: float) -> list[float]:
    """Generic RPL state only; no family, seed, label or attack-marker input."""
    return [
        min(float(row.get("state_low_rank_nonroot_pairs", "0") or 0) / 5.0, 2.0),
        min(float(row.get("state_low_rank_nonroot_senders", "0") or 0) / 5.0, 2.0),
        min(float(row.get("dio_tx_count", "0") or 0) / 30.0, 2.0),
        min(float(row.get("parent_switch_count", "0") or 0) / 10.0, 2.0),
        last_error,
        ddm_alarm,
    ]


class ProfileEnvironment:
    """One ordered target profile with one-window delayed supervised feedback."""

    def __init__(self, source, profile, features):
        self.source = source
        self.profile = sorted(profile, key=lambda row: int(row["window_start_s"]))
        self.features = features

    def reset(self):
        self.model = OnlineGaussianNB(self.features)
        self.model.learn_many(self.source)
        self.ddm = DDM()
        self.pending = None
        self.history = []
        self.index = 0
        self.last_error = 0.0
        self.last_ddm_alarm = 0.0
        return feature_state(self.profile[0], self.last_error, self.last_ddm_alarm)

    def step(self, action: int):
        row = self.profile[self.index]
        prediction = self.model.predict_one(row)
        reward = -0.02 if action == 1 else -0.08 if action == 2 else 0.0
        delayed_label_available = self.pending is not None
        evaluated = None
        if self.pending is not None:
            labelled_row, labelled_prediction = self.pending
            actual = int(labelled_row["window_label"])
            error = int(labelled_prediction != actual)
            ddm_state = self.ddm.update(error)
            self.history.append(labelled_row)
            self.last_error = float(error)
            self.last_ddm_alarm = float(ddm_state == "drift")
            if action == 1:
                self.model.learn_one(labelled_row, actual)
            elif action == 2:
                self.model.reset()
                self.model.learn_many(self.history)
            reward += 2.0 if actual == 1 and labelled_prediction == 1 else 0.25 if actual == 0 and labelled_prediction == 0 else -3.0 if actual == 1 else -1.0
            evaluated = (actual, labelled_prediction)
        self.pending = (row, prediction)
        self.index += 1
        done = self.index == len(self.profile)
        if done:
            labelled_row, labelled_prediction = self.pending
            actual = int(labelled_row["window_label"])
            error = int(labelled_prediction != actual)
            self.last_error = float(error)
            self.last_ddm_alarm = float(self.ddm.update(error) == "drift")
            reward += 2.0 if actual == 1 and labelled_prediction == 1 else 0.25 if actual == 0 and labelled_prediction == 0 else -3.0 if actual == 1 else -1.0
            evaluated = (actual, labelled_prediction)
        next_state = feature_state(self.profile[min(self.index, len(self.profile) - 1)], self.last_error, self.last_ddm_alarm)
        record = {
            "family": row["family"], "mode": row["mode"], "seed": row["seed"],
            "window_start_s": int(row["window_start_s"]), "window_label": int(row["window_label"]),
            "prediction": prediction, "action": ACTION_NAMES[action],
            "delayed_label_available": int(delayed_label_available), "reward": round(reward, 4),
            "ddm_alarm": int(self.last_ddm_alarm), "state": json.dumps(feature_state(row, self.last_error, self.last_ddm_alarm)),
        }
        return next_state, reward, done, record, evaluated


class QNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(STATE_SIZE, 24), nn.ReLU(), nn.Linear(24, ACTION_COUNT))

    def forward(self, values):
        return self.layers(values)


class DefenderAgent:
    def __init__(self, algorithm: str, seed: int):
        self.algorithm = algorithm
        self.rng = random.Random(seed)
        torch.manual_seed(seed)
        self.online = QNetwork()
        self.target = QNetwork()
        self.target.load_state_dict(self.online.state_dict())
        self.optimiser = torch.optim.Adam(self.online.parameters(), lr=0.003)
        self.memory = deque(maxlen=512)
        self.steps = 0

    def action(self, state, epsilon: float) -> int:
        if self.rng.random() < epsilon:
            return self.rng.randrange(ACTION_COUNT)
        with torch.no_grad():
            return int(torch.argmax(self.online(torch.tensor([state], dtype=torch.float32))).item())

    def learn(self, transition) -> None:
        self.memory.append(transition)
        if len(self.memory) < 16:
            return
        batch = self.rng.sample(self.memory, 16)
        states = torch.tensor([item[0] for item in batch], dtype=torch.float32)
        actions = torch.tensor([item[1] for item in batch], dtype=torch.int64).unsqueeze(1)
        rewards = torch.tensor([item[2] for item in batch], dtype=torch.float32)
        next_states = torch.tensor([item[3] for item in batch], dtype=torch.float32)
        dones = torch.tensor([item[4] for item in batch], dtype=torch.float32)
        current = self.online(states).gather(1, actions).squeeze(1)
        with torch.no_grad():
            if self.algorithm == "ddqn":
                next_actions = self.online(next_states).argmax(dim=1, keepdim=True)
                future = self.target(next_states).gather(1, next_actions).squeeze(1)
            else:
                future = self.target(next_states).max(dim=1).values
            expected = rewards + 0.9 * future * (1 - dones)
        loss = nn.functional.smooth_l1_loss(current, expected)
        self.optimiser.zero_grad()
        loss.backward()
        self.optimiser.step()
        self.steps += 1
        if self.steps % 20 == 0:
            self.target.load_state_dict(self.online.state_dict())


class ProfileAdversary:
    """Tabular Q-learning profile selector; reward is defender episode loss."""

    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.q = {family: 0.0 for family in ("sinkhole", "sybil")}

    def select(self, epsilon: float) -> str:
        if self.rng.random() < epsilon:
            return self.rng.choice(tuple(self.q))
        return max(self.q, key=self.q.get)

    def update(self, family: str, defender_reward: float) -> None:
        adversary_reward = -defender_reward
        self.q[family] += 0.15 * (adversary_reward - self.q[family])


def episode(env, choose_action, learn=None):
    state = env.reset()
    total_reward, trace = 0.0, []
    done = False
    while not done:
        action = choose_action(state)
        next_state, reward, done, record, _ = env.step(action)
        if learn:
            learn((state, action, reward, next_state, float(done)))
        total_reward += reward
        trace.append(record)
        state = next_state
    return total_reward, trace


def aggregate(records, name, algorithm, split):
    tp = sum(int(row["window_label"]) == 1 and int(row["prediction"]) == 1 for row in records)
    tn = sum(int(row["window_label"]) == 0 and int(row["prediction"]) == 0 for row in records)
    fp = sum(int(row["window_label"]) == 0 and int(row["prediction"]) == 1 for row in records)
    fn = sum(int(row["window_label"]) == 1 and int(row["prediction"]) == 0 for row in records)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"split": split, "policy": name, "algorithm": algorithm, "windows": len(records),
            "accuracy": round((tp + tn) / len(records), 4), "precision": round(precision, 4),
            "recall": round(recall, 4), "f1": round(2 * precision * recall / (precision + recall), 4) if precision + recall else 0.0,
            "fpr": round(fp / (fp + tn), 4) if fp + tn else 0.0, "tp": tp, "tn": tn, "fp": fp, "fn": fn}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/data/stream_windows.csv"))
    parser.add_argument("--manifest", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/data/feature_manifest.json"))
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/90 Raw Reproducibility Workspace/adversarial_rl_sybil_v1/results/adversarial_rl"))
    parser.add_argument("--episodes", type=int, default=240)
    args = parser.parse_args()
    rows = read_csv(args.stream)
    features = json.loads(args.manifest.read_text(encoding="utf-8"))["learning_features"]
    source = [row for row in rows if row["family"] == "blackhole" and row["seed"] in TRAIN_SEEDS]
    profiles = {(family, mode, seed): [row for row in rows if row["family"] == family and row["mode"] == mode and row["seed"] == seed]
                for family in ("sinkhole", "sybil") for mode in ("attack", "control") for seed in TRAIN_SEEDS + TEST_SEEDS}
    summaries, all_records, adversary_rows = [], [], []
    for algorithm, seed in (("dqn", 11), ("ddqn", 29)):
        defender = DefenderAgent(algorithm, seed)
        adversary = ProfileAdversary(seed)
        train_counts = Counter()
        for episode_index in range(args.episodes):
            epsilon = max(0.05, 0.6 * (1 - episode_index / args.episodes))
            family = adversary.select(epsilon)
            target_seed = TRAIN_SEEDS[episode_index % len(TRAIN_SEEDS)]
            env = ProfileEnvironment(source, profiles[(family, "attack", target_seed)], features)
            reward, _ = episode(env, lambda state: defender.action(state, epsilon), defender.learn)
            adversary.update(family, reward)
            train_counts[family] += 1
            adversary_rows.append({"algorithm": algorithm, "episode": episode_index + 1, "family": family,
                                   "seed": target_seed, "defender_reward": round(reward, 4),
                                   "adversary_q_sinkhole": round(adversary.q['sinkhole'], 4),
                                   "adversary_q_sybil": round(adversary.q['sybil'], 4)})
        for policy, action_fn in (
            ("static_source", lambda state: 0),
            ("always_incremental", lambda state: 1),
            ("rl_controller", lambda state: defender.action(state, 0.0)),
        ):
            records = []
            for family in ("sinkhole", "sybil"):
                for mode in ("attack", "control"):
                    for target_seed in TEST_SEEDS:
                        env = ProfileEnvironment(source, profiles[(family, mode, target_seed)], features)
                        _, trace = episode(env, action_fn)
                        for row in trace:
                            row.update({"split": "held_out_test", "policy": policy, "algorithm": algorithm})
                        records.extend(trace)
            all_records.extend(records)
            summaries.append(aggregate(records, policy, algorithm, "held_out_test"))
        summaries.append({"split": "training", "policy": "adversarial_profile_selector", "algorithm": algorithm,
                          "windows": args.episodes, "accuracy": "", "precision": "", "recall": "", "f1": "", "fpr": "",
                          "tp": train_counts['sinkhole'], "tn": train_counts['sybil'], "fp": "", "fn": ""})
    write_csv(args.out_dir / "held_out_window_trace.csv", all_records)
    write_csv(args.out_dir / "held_out_summary.csv", summaries)
    write_csv(args.out_dir / "adversary_training_trace.csv", adversary_rows)
    print(f"Wrote local DQN/DDQN results for {args.episodes} adversarial-profile training episodes to {args.out_dir}")


if __name__ == "__main__":
    main()
