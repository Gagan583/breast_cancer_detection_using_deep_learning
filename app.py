# Importing essential libraries and modules

from flask import Flask, render_template, request, Markup
import numpy as np
#import pandas as pd
import os
import requests
import config
import pickle
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# ==============================================================================================
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb
# -------------------------LOADING THE TRAINED MODELS -----------------------------------------------

gmail_list=[]
password_list=[]
gmail_list1=[]
password_list1=[]



#disease_dic= ["Eye Spot","Healthy Leaf","Red Leaf Spot","Redrot","Ring Spot"]



from model_predict2  import pred_skin_disease
from model_predict_unknown  import pred_unknown
# ===============================================================================================
# ------------------------------------ FLASK APP -------------------------------------------------


app = Flask(__name__)

# render home page

@app.route('/')
def home():
    return render_template('login44.html')   


@app.route('/register22',methods=['POST','GET'])
def register22():
    return render_template('register44.html')  

@app.route('/logedin',methods=['POST'])
def logedin():
    
    int_features3 = [str(x) for x in request.form.values()]
    print(int_features3)
    logu=int_features3[0]
    passw=int_features3[1]
   # if int_features2[0]==12345 and int_features2[1]==12345:

    import MySQLdb


# Open database connection
    db = MySQLdb.connect("localhost","root","","ddbb" )

# prepare a cursor object using cursor() method
    cursor = db.cursor()
    cursor.execute("SELECT user FROM user_register")
    result1=cursor.fetchall()
              #print(result1)
              #print(gmail1)
    for row1 in result1:
                      print(row1)
                      print(row1[0])
                      gmail_list.append(str(row1[0]))
                      
                      #gmail_list.append(row1[0])
                      #value1=row1
                      
    print(gmail_list)
    

    cursor1= db.cursor()
    cursor1.execute("SELECT password FROM user_register")
    result2=cursor1.fetchall()
              #print(result1)
              #print(gmail1)
    for row2 in result2:
                      print(row2)
                      print(row2[0])
                      password_list.append(str(row2[0]))
                      
                      #gmail_list.append(row1[0])
                      #value1=row1
                      
    print(password_list)
    print(gmail_list.index(logu))
    print(password_list.index(passw))
    
    if gmail_list.index(logu)==password_list.index(passw):
        return render_template('index.html')
    else:
        return jsonify({'result':'use proper  gmail and password'})
                  
                                               



                          
                     # print(value1[0:])
    
    
    
    

              
              # int_features3[0]==12345 and int_features3[1]==12345:
               #                      return render_template('index.html')
        
@app.route('/register',methods=['POST'])
def register():
    

    int_features2 = [str(x) for x in request.form.values()]
    #print(int_features2)
    #print(int_features2[0])
    #print(int_features2[1])
    r1=int_features2[0]
    print(r1)
    
    r2=int_features2[1]
    print(r2)
    logu1=int_features2[0]
    passw1=int_features2[1]
        
    

    

   # if int_features2[0]==12345 and int_features2[1]==12345:

    import MySQLdb


# Open database connection
    db = MySQLdb.connect("localhost","root",'',"ddbb" )

# prepare a cursor object using cursor() method
    cursor = db.cursor()
    cursor.execute("SELECT user FROM user_register")
    result1=cursor.fetchall()
              #print(result1)
              #print(gmail1)
    for row1 in result1:
                      print(row1)
                      print(row1[0])
                      gmail_list1.append(str(row1[0]))
                      
                      #gmail_list.append(row1[0])
                      #value1=row1
                      
    print(gmail_list1)
    if logu1 in gmail_list1:
                      return jsonify({'result':'this gmail is already in use '})  
    else:

                  #return jsonify({'result':'this  gmail is not registered'})
              

# Prepare SQL query to INSERT a record into the database.
                  sql = "INSERT INTO user_register(user,password) VALUES (%s,%s)"
                  val = (r1, r2)
   
                  try:
   # Execute the SQL command
                                       cursor.execute(sql,val)
   # Commit your changes in the database
                                       db.commit()
                  except:
   # Rollback in case there is any error
                                       db.rollback()

# disconnect from server
                  db.close()
                 # return jsonify({'result':'succesfully registered'})
                  return render_template('login44.html')

                      






#@ app.route('/')
#def home():
#    title = 'Vitamin Deficiency Prediction Based on Skin Disease'
#    return render_template('index.html', title=title)

# render crop recommendation form page
@app.route('/disease-predict', methods=['GET', 'POST'])
def disease_prediction():
    title = 'Breast Cancer Detection System'

    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            return render_template('rust.html', title=title)

        # Process the uploaded file
        img = Image.open(file)
        img.save('output.png')

        prediction1, accuracy1=pred_unknown("output.png")


        if prediction1=="unknown":


              return render_template('error_page.html')

        else:

           print("input is Breast cancer image")



          



        # Make the prediction
        prediction, accuracy = pred_skin_disease("output.png")

        print("Prediction result:", prediction)

        # Disease information for Breast Cancer
        disease_info = {
            "benign": {
                "cause": "Non-cancerous breast tumor; does not spread to other tissues.",
                "treatment": "Usually no treatment needed except regular monitoring; in some cases, surgery may be done to remove the lump.",
                "treatment_cost": {
                    "India": "₹20,000 – ₹80,000 (if surgery required)",
                    "USA": "$3,000 – $10,000 (monitoring/surgery)"
                },
                "best_hospitals": {
                    "India": "AIIMS Delhi, Tata Memorial Hospital (Mumbai), Apollo Hospitals",
                    "USA": "Mayo Clinic, MD Anderson Cancer Center, Johns Hopkins Hospital"
                },
                "global_data": "Benign breast tumors are more common than malignant; they do not affect survival rate.",
                "alternative_treatments": {
                    "Ayurveda": "Herbal medicines, diet regulation",
                    "Homeopathy": "Symptom-based remedies, regular monitoring",
                    "Allopathy": "Surgery if required, regular follow-ups"
                }
            },
            "malignant": {
                "cause": "Cancerous breast tumor that can invade nearby tissue and spread (metastasize) to other parts of the body.",
                "treatment": "Requires immediate medical care; treatments may include surgery, chemotherapy, radiation therapy, hormone therapy, or targeted therapy.",
                "treatment_cost": {
                    "India": "₹3,00,000 – ₹8,00,000 (depending on stage and therapy)",
                    "USA": "$50,000 – $1,50,000 (depending on stage and treatment)"
                },
                "best_hospitals": {
                    "India": "Tata Memorial Hospital (Mumbai), AIIMS Delhi, Apollo Hospitals",
                    "USA": "MD Anderson Cancer Center, Memorial Sloan Kettering, Mayo Clinic"
                },
                "global_data": "Breast cancer is the most common cancer in women worldwide. 5-year survival rate is ~90% if detected early.",
                "alternative_treatments": {
                    "Ayurveda": "Herbal formulations like Ashwagandha, dietary management",
                    "Homeopathy": "Complementary support (not standalone treatment)",
                    "Allopathy": "Surgery, chemotherapy, radiation, immunotherapy"
                }
            }
        }

        # Fetch details based on prediction
        details = disease_info.get(prediction, {})
        cause = details.get("cause", "Unknown condition detected.")
        treatment = details.get("treatment", "No treatment information available.")
        treatment_cost = details.get("treatment_cost", {})
        best_hospitals = details.get("best_hospitals", {})
        global_data = details.get("global_data", "No global data available.")
        alternative_treatments = details.get("alternative_treatments", {})

        # Render the result page
        return render_template(
            'rust-result.html',
            prediction=prediction,
            cause=cause,
            treatment=treatment,
            treatment_cost=treatment_cost,
            best_hospitals=best_hospitals,
            global_data=global_data,
            alternative_treatments=alternative_treatments,
            title="Breast Cancer Information",
            accuracy=accuracy
        )

    # Default page rendering
    return render_template('rust.html', title=title)
from flask import make_response,send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    prediction = request.form.get('prediction')
    cause = request.form.get('cause')
    treatment = request.form.get('treatment')
    treatment_cost_india = request.form.get('treatment_cost_india')
    treatment_cost_usa = request.form.get('treatment_cost_usa')
    best_hospital_india = request.form.get('best_hospital_india')
    best_hospital_usa = request.form.get('best_hospital_usa')
    global_data = request.form.get('global_data')
    ayurveda = request.form.get('ayurveda')
    homeopathy = request.form.get('homeopathy')
    allopathy = request.form.get('allopathy')

    # Create PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Add content
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 100, "Breast Cancer Detection Report")

    p.setFont("Helvetica", 12)
    p.drawString(100, height - 140, f"Disease Prediction: {prediction}")
    p.drawString(100, height - 160, f"Cause: {cause}")
    p.drawString(100, height - 180, f"Treatment: {treatment}")

    # Costs
    p.drawString(100, height - 210, f"Treatment Cost in India: {treatment_cost_india}")
    p.drawString(100, height - 230, f"Treatment Cost in USA: {treatment_cost_usa}")

    # Hospitals
    p.drawString(100, height - 260, f"Best Hospitals in India: {best_hospital_india}")
    p.drawString(100, height - 280, f"Best Hospitals in USA: {best_hospital_usa}")

    # Global Data
    p.drawString(100, height - 310, f"Global Data: {global_data}")

    # Alternative treatments
    p.drawString(100, height - 340, "Alternative Treatments:")
    p.drawString(120, height - 360, f"Ayurveda: {ayurveda}")
    p.drawString(120, height - 380, f"Homeopathy: {homeopathy}")
    p.drawString(120, height - 400, f"Allopathy: {allopathy}")

    p.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Breast_Cancer_Report.pdf",
        mimetype='application/pdf'
    )



# ===============================================================================================
if __name__ == '__main__':
    app.run(debug=True)
