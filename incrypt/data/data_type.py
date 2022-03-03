import numpy as np
import pandas as pd
import pytz

class DataType:

    @staticmethod
    def convert_boolean(b):
        btype = type(b)
        if btype is int:
            return (b != 0)
        elif btype is str:
            if b in ['Y','YES','1',"'1'"]:
                return True
            elif b in ['0',"'0'",'N','NO']:
                return False
        elif (btype is bool) \
            or (btype is np.bool) \
            or (btype is np.bool_) \
            or (btype is np.bool8):
            return b
        else:
            return None

    @staticmethod
    def convert_timestamp(dt):
        if pd.isnull(dt):
            return pd.NaT
        dt = pd.to_datetime(dt, infer_datetime_format=True)
        if pd.isnull(dt):
            return pd.NaT
        elif type(dt) == np.datetime64:
            dt = pd.Timestamp(dt).to_pydatetime()
        if hasattr(dt, 'tzinfo') and pd.isnull(dt.tzinfo):
            dt = pytz.utc.localize(dt)
        return dt