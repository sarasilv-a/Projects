import pandas as pd

# ======================================
def to_csv(pred,path):
    """
    Save predictions to a CSV file
    """
    submission = pd.DataFrame({
        "RowId": range(1, len(pred)+1),
        "Speed_Diff": pred
    })

    submission.to_csv(path, index=False)

# ======================================
def load_data(path):
    """
    Load dataset from a CSV file
    """
    data = pd.read_csv(path, encoding='latin-1')
    return data