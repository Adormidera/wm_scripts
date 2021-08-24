# Window Manager Scripts
This repository contains a set of scripts designed to improve the tilling window manager experience ;D.

## Scripts

### CPU
#### *cpu_usage*
Returns the current CPU usage percent using `top`.

##### Parameters
All the parameters of this script are defined in environment variables.

##### Run Examples
```bash
# Normal
./cpu_usage

# Change alert intervals
ERR_LIMIT=10 ./cpu_usage
```

##### i3wm config
```INI
[cpu]
command=./scripts/cpu_usage
interval=10
ERR_LIMIT=90
WARN_LIMIT=70
ICON=""
ITERATIONS=5
DELAY=0.05
OK_COLOR="#1FC40D"
WARN_COLOR="#FFA600"
ERR_COLOR="#DE1212"
```
