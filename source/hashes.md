# Hashes and closed versions

## The problem

You published version 2 of a protocol. Clients in the field speak it. A month later somebody "fixes" a field in version 2, and now the description and the shipped clients disagree. Nobody notices until something breaks.

A **hash** makes this impossible to do quietly. A hash closes a version. If the important values of a closed version change, the next run fails and says which aggregates differ.

## What a hash covers

A hash is made of the **important** values only: the values of tags marked `important` (see [Tags](tags.md#important)).

![The content hash](images/11_hash.svg)

- Each aggregate has a content hash of its important tags in that version.
- The root stores the combination of all of them: the aggregate hashes sorted, then combined.
- **Left out**: tag names, labels, aggregate names, file names and paths, comments, and every tag that is not `important`.

The reason is freedom. You can rename a file, move an aggregate to another folder, add a label part, add a note. The published meaning did not change, so the hash does not either.

A hash is stored in the declaration of a version:

```
versions
{
    0 = { hash = '27025d7a1482f343d1f2f0bb2865d7055458e172a1ff90dd9b4cccfd4aba3035' };
    1 = { hash = '704dd06e344f8b26bf000ed10194d6f0e856afec347f962900e05a15e1df091b' };
    2;
}
```

Every aggregate that is not deleted in that version stores its own hash in its own file. The root file stores the combined one. A version with a hash on the root but not on some aggregate is an error (`HASH_MUST_BE_ON_EVERY_AGGREGATE`).

## Closed versions

![States of a version](images/10_version_states.svg)

A **closed version** is a root version that stores a hash, and **every version before it**. If version 3 has a hash, versions 0, 1, 2 and 3 are closed. History does not have holes.

What is closed:

- Its important values do not change. Any change fails the check.
- `wizard delete version` refuses it.
- `wizard delete aggregate` and `wizard copy aggregate` refuse an aggregate that it contains.
- `wizard create tag` and the other statement commands write into the **last open version**, so a closed version is never touched by accident.

What is still allowed in a closed version: unimportant tags, labels, comments. They are outside the hash.

## Creating and removing a hash

```
wizard create hash;           // the last version
wizard create hash 3;         // version 3
wizard create hash 3, 4;      // both
wizard delete hash 3;         // open version 3 again, on purpose
```

`wizard create version` always adds a new **open** version after the closed ones. The usual rhythm is: write into the open version, check, `wizard create hash` to publish, `wizard create version` to start the next.

To change a closed version, first delete its hash. This is a deliberate act: you cannot do it by accident, and you must say it with a command.

### force

```
wizard create hash 3 force;
wizard delete hash 3 force;
```

Normally Galimatron checks the stored hash of every version before the wizard runs. If a stored hash does not match because you edited by hand, the run fails, and the message names the version and the aggregates.

`force` is for the version you name. `create hash ... force` stores the hash of the important tags *as they are now*. `delete hash ... force` removes a hash that does not match. Use it when you know the data is right and the hash is stale. Versions you do not name are still checked.

## The hash and your XSLT

A hash is taken from the data **after** the wizard and **after** your language XSLT. When `create hash` and an XSLT that generates values (a new uuid) run together, the hash covers the generated values. The [UUID protocol](uuid-protocol.md) does this at step 3.

Your XSLT must not break a closed version. What if it must? For example a generator changes a type name that the closed version holds. Galimatron has an answer: the **seal**.

![The seal](images/19_seal.svg)

After your XSLT Galimatron compares the text before and after. Where the XSLT changed a value that belongs to a closed version, it **moves the change to the first open version after it**, and creates that version when it does not exist. The closed version keeps its text, and its hash stays true.

The effect for you: an XSLT can be written as if it edits the whole description, and history is still safe. The change shows up in the first open version, where you can see it and publish it.

Then the validation runs again. A user XSLT does not rewrite a hash, so a hash that no longer matches fails the run, and nothing is written.

## What Galimatron checks about hashes

| Rule | Error |
|---|---|
| The stored hash of a version equals the one computed now. | `HASH_DOES_NOT_MATCH`, naming the aggregates of each differing version, then a version that differs only in the root. |
| A version with a hash has it on the root and on every live aggregate. | `HASH_MUST_BE_ON_EVERY_AGGREGATE`, naming each declaration where it is absent. |
| `create hash` and `delete hash` name versions that exist. | `WIZARD_CREATE_HASH_VERSION_MUST_EXIST`, `WIZARD_DELETE_HASH_VERSION_MUST_EXIST` |

A version with no hash is not checked.
