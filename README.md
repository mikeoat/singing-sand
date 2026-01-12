# DISCRETE ELEMENT METHOD IMPLEMENTATION OF THE SINGING SAND PHENOMENON FOR USE IN SOUND SYNTHESIS
### A project by Mike McDonald
### Done for my Electronic Production and Design capstone project at Berklee College of Music.
### Associated paper pending publishing
This project was created using YADE 2023.02a and Python 3.11.2. Because this project is
a collection of scripts that interact with different libraries, there isn't necessarily a
license outside of "don't copy what I've written exactly." I have no interest in protecting
the underlying principles of this project.

# INSTRUCTIONS FOR USAGE
1. Ensure at least YADE 2023.02a is installed along with Python 3.11.2
2. Make desired edits to dune.py
3. Run dune.py using YADE
4. Ensure output data is as expected
5. Run sample_generation.py
6. Close output plot and listen to audio files!

# AUDIO POST PROCESSING RECOMMENDATIONS
The resonance produced by this simulation lasts for less than 500ms, so it would be wise to
loop a section of the output file upon itself. The best place in the file to do this is just
after the initial transient ends

# SPECIFICATIONS
The DEM simulation alone takes about 2 and a half days to run on a Debian Trixie Stable system
with an AMD Ryzen 7 5800X Processor, Nvidia GeForce RTX 2060 GPU with 6GB of VRAM, and 32GB of
RAM. I decided to run the simulation with all 16 logical and physical cores of my processor,
using `yade -j16 dune.py`.
This project has not been tested on older versions of YADE or Python, though I suspect older
versions of Python 3 should work.

# FILE INFORMATION
## dune.py
Most of what is going on in this file should be well-explained by variable names, but I'll
go over it just in case.
| VARIABLE NAME | FUNCTION                                                                           | RECOMMENDED VALUE |
| ------------- | --------                                                                           | ----------------- |
| scalingFactor | number that is multiplied by various values to make the simulation more easily run | 40                |
| numParticles  | particle count                                                                     | 10000             |
| width         | width of the ramp                                                                  | 5e-2              |
| widthUnit     | used for data collection window definition consistency                             | width/10          |
| length        | length of the ramp along the y axis                                                | 1.82e-1           |
| lengthUnit    | used for data collection window definition consistency                             | length/10         |
| height        | ending point of the ramp along z, should be negative for a declining ramp          | -1.05e-1          |
| one           | functions as a scaled 1 for use in the creation of objects                         | 1e-1              |
| r             | the average radius of generated grains                                             | 1.5e-4            |
| h             | initial height of the grain pile                                                   | one * 0.6         |

The file itself is separated into a couple sections:
1. Materials, where objects' materials are defined
2. Number Definitions, which is outlined above
3. Creating Objects In YADE, where all objects are created based on number definitions
4. Run Simulation, where the simulation is run for a given simLength
5. Function Definitions, where functions are defined to do with data collection and object movement

## sample_generation.py
The process behind what happens in this file is better explained in [my paper](https://mote.moe). Because of this, I will only go over some important things:
- There is a magic number on line 22 that *should* gel well with whatever values you throw at it, but just in case, it's based on the `PWaveTimeStep()` value taken from YADE
- All `savePath` variables on lines 27-34 can point to different locations for each dataset if desired
- The audio files will only be generated **after** the generated plot is closed

# CONCLUSION
That about does it! If you encounter any issues, feel free to open an issue on this repository and/or email me at mgmcd04@tutanota.com
