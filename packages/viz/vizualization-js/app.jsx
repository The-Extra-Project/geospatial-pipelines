import React, { useState, useEffect } from 'react';
import { createRoot } from "react-dom/client";
import { Deck ,COORDINATE_SYSTEM } from "@deck.gl/core";
import { PointCloudLayer } from "@deck.gl/layers";
import { Card, Button, Slider, } from "@mui/material"
const test_file_vizualition = "./LHD_FXX_0633_6867_PTS_C_LAMB93_IGN69.copc.laz"
import { PLYLoader } from "@loaders.gl/ply"
import {Tiles3DLoader} from "@loaders.gl/3d-tiles"

const transitionInterpolator = new LinearInterpolator(['rotationOrbit']);

const INITIAL_VIEW_STATE = {
    target: [0, 0, 0],
    rotationX: 0,
    rotationOrbit: 0,
    minZoom: 0,
    maxZoom: 10,
    zoom: 1,
};

const INITIAL_CONTROL_SET = {
    uploaded: false,
    Zoom: 10
}

const deckLayer = new Deck({
initialViewState:  {    
longitude: 122.45,
latitude: 37.78,
zoom: 12

}
// controller: true,
// layers: [
//     new ScatterplotLayer(self.)
// ]

},
)

function displayOptionBox() {
    return (
        <>
            <div class="flex flex-col h-screen">
                <Card>
                    <Button class="w-full mb-4">Upload</Button>
                    <Slider size="large" defaultValue={10}>Zoom</Slider>

                </Card>
            </div>
        </>
    )
}
transitionInterpolator = new LinearInterpolator(['rotationOrbit']);
export default function App({ onLoad }) {
    const [uploaded, NotUploaded] = useState(INITIAL_VIEW_STATE);
    const [currenView, updatedView] = useState(false)

    useEffect(() => {

        if (!isLoaded) {
            return;
        }
        const rotateCamera = () => {
            updatedView(
                viewPoint => (
                    {
                        ...viewPoint,
                        rotationOrbit: viewPoint.rotationOrbit + 60,
                        transitionDuration: 2400,
                        transitionInterpolator,
                        onTransitionEnd: rotateCamera
                    }));
        };
        rotateCamera();
    }, [isLoaded]);

    const onDataLoad = ({header}) => {
        if(header.boundingBox) {
            // for the description of the bounding box 
            // this can be passed from the las /PLY information file 
            const [mins,max] = header.boundingBox;
            updateViewState(
                {
                    ...INITIAL_VIEW_STATE,
                    target: [(mins[0] + maxs[0]) / 2, (mins[1] + maxs[1]) / 2, (mins[2] + maxs[2]) / 2],
                    /* global window */
                    zoom: Math.log2(window.innerWidth / (maxs[0] - mins[0])) - 1
                }
            );
        setIsLoaded(true);
        }

        if(onLoad) {
            onLoad({count: header.vertexCount, progress: 1});
        }
    };

    const layers = [
        new PointCloudLayer({
            id: 'laz example point cloud layer',
            data: test_file_vizualition,
            onDataLoad,
            coordinateSystem: COORDINATE_SYSTEM.CARTESIAN,
            getnormal: [0, 1, 0],      
            getColor: [255, 210, 10],      
            opacity: 0.5,      
            pointSize: 0.5,
        })
    ]


    return (<>
        <DeckGL
            views={new OrbitView({ orbitAxis: 'Y', fov: 50 })}
            viewState={viewState}
            controller={true}
            onViewStateChange={v => updateViewState(v.viewState)}
            layers={layers}
            parameters={{
                clearColor: [0.93, 0.86, 0.81, 1]
            }}
        />
    </>
    )
    


}




export function renderToDOM(container) {
    createRoot(container).render(<App />);
}
