# File Information ---------------------------------------------
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 
# 	File Name: test_vubernetes.py
#
# 	File Description: Test file for vubernetes
# 
# 	File History:
# 		- 2022-08-02: Created by Rohit S.
# . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 

# Imports --------------------------------------------------------
import pytest
from vubernetes import Vubernetes


# Global Variables -----------------------------------------------

# Class Declarations ---------------------------------------------

# Function Declarations ------------------------------------------
@pytest.mark.basic
def test_bookinfo():
    v = Vubernetes('./test_files/bookinfo.yaml')

@pytest.mark.basic
def test_grafana():
    v = Vubernetes('./test_files/grafana.yaml')


@pytest.mark.failure
def test_parseYamlFail():
    with pytest.raises(Exception):
        v = Vubernetes('./test_files/not-a-file.yaml')
