Flag `--show-root` selected, but no name for the root set. 
Rendering the tree as if `--show-root=False` 

To show the root name at the top of the rendered tree

option 1: pass it along with a call to this command and try again. 
```bash
treebuild harvest text --root <name_goes_here> --show-root
```

option 2: set it such that it persists for future calls 
```bash 
treebuild seed <name_goes_here>
treebuild harvest text 
```
---- 

