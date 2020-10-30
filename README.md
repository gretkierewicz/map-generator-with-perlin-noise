# gret_sandbox

Project of map generator.
Main reason - getting some fun with arrays and visualisation of data. 
But also, getting know how to use multiprocessing, file management and many other.

## Features: 

* [x] **Noise Generator**
    * [x] Basic generation and visualization of noise array
        * [x] Basic levels for better visualisation of surface topology
        * [x] Colors of levels for even better topology visualization
            * [x] Additional controls (sea, plains and hills levels)
            * [x] Scrolling option for bigger maps
                * [x] Drag and drop the map
            * [ ] Zoom
    * [x] Basic controls for noise parameters (scale, octaves, persistence, base, factor)
        * [ ] Array offsetting
    * [x] Dynamically controlled additional noise arrays for more complex topologies

* [x] **Gradient**
    * [x] Basic (circle) gradient 
        * [ ] Option to choose between circle and square pattern
    * [x] Controls for pattern parameters

* [x] **Other**
    * [x] Multiprocessing for faster generation of big arrays
    * [x] Handling different events (resize window, control's value change)
    * [ ] Generation of additional topology details (biomes, rivers, lakes)
    * [ ] Saving setup, profiles
    * [ ] Export/Import of arrays/maps

## Screenshots:

![x](/images/screen%2030.10.2020%20resize%20and%20scrolling%20added.png)