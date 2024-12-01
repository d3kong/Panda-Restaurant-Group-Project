import os
import pandas
import numpy as np
import CardNumberCatcher as cnc
checkIn = "Checkin"
transaction = "Transaction"
crd = cnc.Card_Number_Catcher(checkIn, transaction)
crd.print2()