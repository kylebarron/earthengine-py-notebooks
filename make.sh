#! /usr/bin/env bash

# Remove existing notebooks
rm Algorithms/*.ipynb
rm Array/*.ipynb
rm AssetManagement/*.ipynb
rm Basemaps/*.ipynb
rm Datasets/*.ipynb
rm FeatureCollection/*.ipynb
rm Filter/*.ipynb
rm Gena/*.ipynb
rm GetStarted/*.ipynb
rm HowEarthEngineWorks/*.ipynb
rm Image/*.ipynb
rm ImageCollection/*.ipynb
rm JavaScripts/*.ipynb
rm Join/*.ipynb
rm MachineLearning/*.ipynb
rm NAIP/*.ipynb
rm Reducer/*.ipynb
rm Tutorials/*.ipynb
rm Visualization/*.ipynb

# Create new notebooks
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Algorithms/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Array/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb AssetManagement/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Basemaps/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Datasets/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb FeatureCollection/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Filter/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Gena/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb GetStarted/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb HowEarthEngineWorks/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Image/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb ImageCollection/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb JavaScripts/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Join/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb MachineLearning/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb NAIP/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Reducer/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Tutorials/*.py
python Template/convert_to_pydeck.py -t Template/pydeck_template.ipynb Visualization/*.py
