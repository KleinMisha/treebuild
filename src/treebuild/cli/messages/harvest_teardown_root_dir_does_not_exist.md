Cannot dematerialize non-existing root directory: {root_dir}. 

Check that you scaffolded the tree prior

```bash 
treebuild harvest scaffold 
```

Check that you supplied the correct location for the root directory (must be the same as used during scaffolding)

```bash
# If you scaffolded as follows ... 
treebuild harvest scaffold --location <path/to/root/dir>

# then you remove the scaffold by calling 
treebuild harvest teardown --location <path/to/root/dir>
```
----

