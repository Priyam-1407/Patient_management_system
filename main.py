from fastapi import FastAPI, Path, HTTPException, Query
import json
from fastapi.responses import JSONResponse
from typing import Annotated, Literal

from pydantic import BaseModel, Field,computed_field
app=FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., title="Patient ID", description="Unique identifier for the patient", example="P001")]
    name: Annotated[str, Field(..., title="Patient Name", description="Full name of the patient", example="John Doe")]
    city:Annotated[str, Field(..., title="City", description="City of residence", example="New York")]
    age: Annotated[int,Field(...,gt=0,lt=120, title="Age", description="Age of the patient", example=30)]
    gender: Annotated[Literal["male", "female", "other"], Field(..., title="Gender", description="Gender of the patient", example="male")]
    height: Annotated[float, Field(...,gt=0, title="Height", description="Height of the patient in m", example=1.75)]
    weight: Annotated[float, Field(...,gt=0, title="Weight", description="Weight of the patient in kg", example=70.0)]
    @computed_field
    @property
    def bmi(self) -> float:
        bmi=round(self.weight / ((self.height) ** 2),2)
        return bmi

    
    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi < 18.5:
            return "Underweight"    
        elif 18.5 <= self.bmi < 25:
            return "Normal weight"  
        elif 25 <= self.bmi < 30:   
            return "Overweight"
        else:
            return "Obesity"

    
    

def load_data():
    with open("patients.json","r") as f:
        data=json.load(f)
    return data
def save_data(data):
    with open("patients.json","w") as f:
        json.dump(data,f)

@app.get("/")
def hello():
    return {'message':'Patient Management System API'}

@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage your patient records'}

@app.get("/view_patients")
def view_patients():
    data=load_data()
    return data
#path parameter 
@app.get("/patient/{patient_id}") 
def patients_data(patient_id:str=Path(...,#path parameter is mandatory
                                        title="Patient ID", #title for documentation
                                        description="Unique identifier for the patient", #description for documentation
                                        example="P001")): #example value for documentation
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    
    raise HTTPException(status_code=404, detail="Patient not found" )
@app.get('/sort')
def sort_patients(sort_by:str=Query(...,description="Sort on the basis of height , weight or bmi",),order:str=Query("asc",description="Sort order: asc for ascending, desc for descending")):
    valid_fields=["height","weight","bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Valid fields are: {', '.join(valid_fields)}")
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400, detail="Invalid sort order. Valid orders are: asc, desc")
    data=load_data()
    sort_order=True if order=="desc" else False
    sorted_data=sorted(data.items(), key=lambda x: x[1][sort_by], reverse=(sort_order))
    return dict(sorted_data)

@app.post("/create")
def create_pateint(patient:Patient):
    #load existing data
    # check if the patient id already exists
    #if not then add the new patient to the data and save it back to the file
    data=load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    
    data[patient.id]=patient.model_dump(exclude=["id"],mode="json")#exclude id from the patient data as it is already used as the key in the dictionary
    #save it to python dictionary to json file
    save_data(data)
    return JSONResponse (status_code=201, content={"message": "Patient created successfully"})

    