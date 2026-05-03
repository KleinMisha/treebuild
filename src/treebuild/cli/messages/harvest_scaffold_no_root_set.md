Must set the name of the root directory before materializing the scaffold.

option 1: pass it along with a call to this command and try again. 
```bash
treebuild harvest scaffold --root <name_goes_here>
```

option 2: set it such that it persists for future calls 
```bash 
treebuild seed <name_goes_here>
treebuild harvest scaffold 
```
--- 
