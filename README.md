# PY_NTNDA_Viewer 2020.02.26

PY_NTNDA_Viewer is Python code that is similar to the Java EPICS_NTNDA_Viewer that comes with areaDector.

## Status

This is almost ready for prime time.

There are currently 2 versions:

1) P4P_NTNDA_Viewer.py 
This uses **p4p**.
2) PVAPY_NTNDA_Viewer.py
This uses **pvapy**.
**pvapy** is not available on windows and does not provide connect/disconnect notification.


## Running the example

Note that my computer is using fedora 30, which also means python3.

### Starting simDetector

Start an IOC running the simDetector.
For example I start it as follows

    mrk> pwd
    /home/epics7/areaDetector/ADSimDetector/iocs/simDetectorIOC/iocBoot/iocSimDetector
    mrk> ./start_epics

### Start a display manager

At least the following choices are available: **medm**, **edm**, **pydm**, and **css**.
For any choice the display file, with name **simDetector**, to load is located in
**areaDetector/ADSimDetector/simDetectorApp/op**

For example to use **medm** I have the files **setEnv** and **startSimDetector**, which are:

    export PATH=$PATH:/home/epics7/extensions/bin/${EPICS_HOST_ARCH}
    export EPICS_DISPLAY_PATH=/home/epics7/areaDetector/ADCore/ADApp/op/adl
    export EPICS_DISPLAY_PATH=${EPICS_DISPLAY_PATH}:/home/epics7/areaDetector/pvaDriver/pvaDriverApp/op/adl
    export EPICS_DISPLAY_PATH=${EPICS_DISPLAY_PATH}:/home/epics7/areaDetector/ADSimDetector/simDetectorApp/op/adl
    export EPICS_CA_MAX_ARRAY_BYTES=40000000

and

    source ./setEnv
    medm  -x -macro "P=13SIM1:,R=cam1:" simDetector.adl 

then I just enter

    ./startSimDetector



### start P4P_NTNDA_Viewer or PVAPY_NTNDA_Viewer

The channelName can be specified in three ways:

1) Via environment variable **EPICS_NTNDA_VIEWER_CHANNELNAME**.
2) As a command line argument.
3) By entering it via the viewer when in stop mode.

In order to use the codec support from **areaDetector** you must have
a path to **areaDetector/ADSupport/lib...** defined.
The details differ between windows and linux or macos.

An example is **exampleStartP4P**, which uses **p4p** for communication with the simDetector.

    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/epics7/areaDetector/ADSupport/lib/linux-x86_64
    export EPICS_NTNDA_VIEWER_CHANNELNAME="13SIM1:Pva1:Image"
    python P4P_NTNDA_Viewer.py


I start it via

    mrk> pwd
    /home/epics7/modules/PY_NTNDA_Viewer
    mrk> ./exampleStartP4P

You will see errors if You have not installed all the python packages required.
If it shows no errors click connect and start.

Then run whatever opi tool you use to control the simDetector.
Then select plugins All and enable the PVA1 plugin.
Then click connect and then start.

You should see images being displayed.

**exampleStartPVAPY** starts **PVAPY_NTNDA_Viewer.py**, which uses **pvapy** for communication with the simDetector.

## Required python modules

You must have python and pip installed.
I am using ferora core 30 and it has python3 and pip3 installed.

The other python modules can be installed via **pip install ...**

For example I can issue the command

    sudo pip install numpy

The following shows all installed python modules

    pip list

The following is a list of modules required by PY_NTNDA_Viewer

1) numpy
2) PyQt5
3) PyQt5-sip
4) QtPy
5) p4p or pvapy
6) pyqtgraph


## Other things to try

### pixel data types

In the display manager **simDetector** window try the various **Data type**s.
The default is **Uint8**.

Now select **Int8**.
This works just like **Uint8**.

Now select **Int16** and also set **Gain** to 255.
This works. **UInt16** also works.

I think that **Int32**, **UInt32**, **Int64**, **UInt64**, **Float32**, and **Float64** also work.
But it is not easy to test.


### color mode

Set **Color mode** to **Mono** or **RGB1** or **RGB2** or **RGB3** 
These should all work.

### codec

Select plugins All.
On the new window set the Port for PVA1 to **CODEC1**.
Then on the line for CODEC1 click on **More**.
In the new window set Enable to **Enable**.

You should see what you saw before.

Next select Compressor.
You should see what you did before,
except that on the PY_NTNDA_Viewer window you will see that the compressed size is much less
than the uncompressed size.


### Performance

For a 1024x1024 image:

1) NDPVa generates 196 frames/sec
2) EPICS_NTDA_Viewer handles 140 frames/second
3) NTDA_Viewer only does about 20 frames/second.

For a 512x512 image:

1) NDPVa generates 196 frames/sec
2) EPICS_NTDA_Viewer handles 193 frames/second
3) NTDA_Viewer does about 135 frames/second.


I did some searching on-line and saw:


    The ImageView class can also be instantiated directly and embedded in Qt applications.
    Instances of ImageItem can be used inside a ViewBox or GraphicsView.
    For higher performance, use RawImageWidget.
    Any of these classes are acceptable for displaying video by calling setImage() to display a new frame.
    To increase performance, the image processing system uses scipy.weave to produce compiled libraries.
    If your computer has a compiler available, weave will automatically attempt to build the libraries it needs on demand.
    If this fails, then the slower pure-python methods will be used instead.


But for python3, **weave** is no longer supported 

It is possible that ImageJ is not really displaying 140/193 frames/s because the actual drawing operation may be deferred and throttled just like Qt. But the code thinks it is doing the faster rate because is not waiting for the display to update.

## Theory of Operation

PY_NTNDA_Viewer provides support for an NTNDArray supported by **areaDetector/ADCore/ADApp/ntndArrayConverterSrc**.

PY_NTNDA_Viewer has the following python modules:

1) P4P_NTNDA_Viewer.py : a channel provider that uses p4p to connect to an NTNDArray
2) PVAPY_NTNDA_Viewer.py : a channel provider that uses pvapy to connect to an NTNDArray
3) NTNDA_Viewer.py : The code that displays images provides by a channel provider.

**NTNDA_Viewer.py** defines the following python classes:

* NTNDA_Channel_Provider : a base class that a channel provider must implement
* Image_Display : a class that displays an image
* ImageControl: a class that calls Image_Display and provides sliders and zoom.
* NTNDA_Viewer : A class that receives images from a channel provider.
It supports decompression and conversion of 1d numpy arrays to either 2d or 3d numpy arrays.
It then calls ImageControl with the 2d or 3d numpy array.


### An NTDAArray has the following structure:

    epics:nt/NTNDArray:1.0
        union value                   // provider must present this a a 1d numpy array of one of the following types
            boolean[] booleanValue    // not used by PY_NTNDA_Viewer
            byte[] byteValue
            short[] shortValue
            int[] intValue
            long[] longValue
            ubyte[] ubyteValue
            ushort[] ushortValue
            uint[] uintValue
            ulong[] ulongValue
            float[] floatValue
            double[] doubleValue
        codec_t codec
            string name
            any parameters
        long compressedSize
        long uncompressedSize
        dimension_t[] dimension
            dimension_t
                int size
                // other fields not used by PY_NTNDA_Viewer
        // other fields not used by PY_NTNDA_Viewer

### value

The channel provider, e.g. **PVAPYProvider** or **P4PProvider**, must provide this as a 1d numpy array.
The mapping between the numpy dtype and the value type is:

    value type     dtype
    ----------     -----
    byte           int8
    short          int16
    int            int32
    long           int64
    ubyte          uint8
    ushort         uint16
    uint           uint32
    ulong          uint64
    float          float32
    double         float64

### codec

**codec** is always of the form

    codec_t codec
        string name jpeg   // must be one  of "", jpeg, blosc, lz4, or bslz4
        any parameters
            int  1         // indicates dtype for each pixel

If **codec.name** is an empty string then **value** is not compressed.
In this case the rest of this section does not apply.

The code in **NTNDA_Viewer.decompress** decompresses the data in **value** and creates a 1d numpy array.
It first checks that the name is jpeg, blosc, lz4, or bslz4.
It is is not it generates an exception that results in a error message.

If the name is one of the types supported decompression it uses the following:

* The compressedSize and uncompressedSize from the NTNDArray passed by the channel provider
* One of the shared libraries from compressedSize: **blosc**, **decompressJPEG**,or **bitshuffle**.
* **codec.parameter.int**


**codec.parameter.int** is an integer representing the data types for the value
Note that for jpeg only dtype byte and ubyte are supported.
For the other codec types all dtypes are supported.

The mapping from the integer value to the numpy dtype is:

        if typevalue== 1 : dtype = "int8"
        elif typevalue== 5 : dtype = "uint"
        elif typevalue== 2 : dtype = "int16"
        elif typevalue== 6 : dtype = "uint16"
        elif typevalue== 3 : dtype = "int32"
        elif typevalue== 7 : dtype = "uint32"
        elif typevalue== 4 : dtype = "int64"
        elif typevalue== 8 : dtype = "uint64"
        elif typevalue== 9 : dtype = "float32"
        elif typevalue== 10 : dtype = "float64"
        else : raise Exception('decompress mapIntToType failed')

The final result is the compressed data in **value** is converted to a 1d numpy array with the correct dtype.

### dimension

This is used by **NTNDA_Viewer.dataToImage** to transform the 1d numpy array to either a 2d or 3d numpy array.
If the number of dimensions is 2 than the data is for a monocromatic image.
If the dimension is 3 then one of the dimensions must have size 3 and must be RBG data.
Note also that areaDetector and numpy use different conventions for **x** and **y**.
Thus **NTNDA_Viewer.dataToImage** transposes x and y. 

