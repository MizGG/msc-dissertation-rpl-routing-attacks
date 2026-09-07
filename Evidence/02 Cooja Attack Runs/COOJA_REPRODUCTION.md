# Rebuilding a Cooja Scenario

This folder is designed to let a reviewer inspect a saved run or rebuild a scenario using a separate Contiki-NG installation.

## Required software

- Java and the build dependencies required by Contiki-NG/Cooja.
- GNU Make 4 or newer, available as `gmake` on the command line. On macOS, install it with Homebrew: `brew install make`.
- A Contiki-NG checkout at commit `2d20e000c24043c750d0ec9d338b42e3e7d92463`.
- Cooja launched from that same checkout.

The repository does not redistribute Contiki-NG itself. Obtain it separately from its official repository, then check out the recorded commit.

## Apply the experiment changes

From the Contiki-NG checkout:

```sh
git checkout 2d20e000c24043c750d0ec9d338b42e3e7d92463
git apply "/path/to/reviewer-package/Evidence/07 Source Code and Contiki Changes/Contiki NG Modifications/contiki-ng-dissertation-current.patch"
```

The patch changes the RPL implementation and the RPL-UDP example Makefile used by the experiment. Do not apply it to an unrelated Contiki-NG revision.

## Open a scenario

1. Start Cooja from the patched Contiki-NG checkout.
2. Open one `.csc` file from an attack's `Configurations` directory. For example, begin with `Sybil/Configurations/SYBIL_ATTACK_N16_SEED123456.csc`.
3. When Cooja asks for the Contiki-NG directory, select the patched checkout.
4. Cooja resolves the attack source from the sibling `code` directory and passes its Contiki-NG location to `gmake` during compilation.
5. Run the 540-second simulation. The fixed seed is embedded in the configuration.

Each attack has five attack seeds and five matched control seeds. The saved `Raw Runs` directories are the original evidence; reruns are for inspection and may vary if toolchain versions differ.

## Directory convention

Every attack uses the same layout:

```text
Attack name/
  Configurations/  Cooja .csc files
  code/            attack and control application source
  Raw Runs/        saved traces and logs
```

The standard UDP client and server are referenced from the Contiki-NG checkout in most scenarios. Sinkhole and Blackhole retain local copies in `code` because those scenarios use locally patched application variants.
