from flask import Flask, render_template, request
import pandas as pd
import os
import random
import sqlite3

# Initialize Flask app
app = Flask(__name__)

# Set the upload folder path to 'static/uploads'
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set up SQLite database connection
connection = sqlite3.connect('DataBase.db', check_same_thread=False)
cursor = connection.cursor()

# Create the user table if it doesn't exist
command = """CREATE TABLE IF NOT EXISTS user(roll TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)
connection.commit()

# Function to search for the roll number in multiple CSV files
def search_roll_no(roll_no, csv_folder):
    results = []
    # Loop through all files in the folder
    for file_name in os.listdir(csv_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(csv_folder, file_name)
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            
            # Search for the roll number in the DataFrame
            matched_rows = df[df['Roll_num'] == roll_no]
            
            # If there are matching rows, store them along with the file name
            if not matched_rows.empty:
                results.append(file_name)
                results.append(matched_rows.values[0])
                break
    
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adminlog', methods=['GET', 'POST'])
def adminlog():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if name == 'admin' and password == 'admin':
            return render_template('adminlog.html', msg='Successfully logged in')
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided, Try Again')
    return render_template('index.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':
        roll = request.form['roll']
        password = request.form['password']

        query = "SELECT * FROM user WHERE roll = ? AND password= ?"
        cursor.execute(query, (roll, password))
        result = cursor.fetchall()

        if result:
            # Specify the folder containing your CSV files and the roll number to search
            csv_folder = 'static/uploads'
            roll_no_to_search = roll

            # Search for the roll number
            matched_results = search_roll_no(roll_no_to_search, csv_folder)

            # Display the results
            if matched_results:
                file_name = matched_results[0].replace('_', ' ')
                file_name = file_name.replace('.csv', '')
                return render_template('userlog.html', rows=matched_results[1], result=result[0], file_name=file_name)
            else:
                print("Roll number not found in any file.")
                return render_template('userlog.html', msg="Roll number not found in any file.")
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided, Try Again')

    return render_template('index.html')

@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':
        roll = request.form['roll']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']

        cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?)", (roll, password, mobile, email))
        connection.commit()

        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/allocate', methods=['GET', 'POST'])
def allocate():
    if request.method == 'POST':
        # Get all uploaded files
        # uploaded_files = request.files.getlist('files[]')
        
        # Check if any files were uploaded
        # if not uploaded_files or all(for file in uploaded_files):
            # return render_template('adminlog.html', msg='Please upload the required files.')
        # print(uploaded_files)
        # Save each file to the 'static/uploads' folder
        file1 = request.files['file1']
        file2 = request.files['file2']
        file3 = request.files['file3']
        file4 = request.files['file4']
        file5 = request.files['file5']

        files = [file1, file2, file3, file4, file5]

        file_paths = []

        for file in files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            file_paths.append(file_path)


        print(files,file_paths)
        # Now read the saved CSV files for further processing
        # Assuming the order in which they are uploaded is the order to be processed
        cs, ee, cv, mc, tl = (pd.read_csv(file_path) for file_path in file_paths)

        # Further processing (your existing code)
        nm = tl['Lecturer_name']
        List = []
        for n in nm:
            List.append(n)
        LecturerList = random.sample(List, 16)
        csn = cs['Student_name']
        csr = cs['Roll_num']

        een = ee['Student_name']
        eer = ee['Roll_num']

        cvn = cv['Student_name']
        cvr = cv['Roll_num']

        mcn = mc['Student_name']
        mcr = mc['Roll_num']

        names = []
        roll = []
        bench = []

        total = int(len(een) + len(csn) + len(cvn) + len(mcn))
        for i in range(1, total + 1):
            bench.append('BN{:04}'.format(i))

        for i in range(int(len(csn) / 5)):
            st = 5 * i
            sp = 5 * (i + 1)

            for i in csn[st:sp]:
                names.append(i)

            for i in een[st:sp]:
                names.append(i)

            for i in cvn[st:sp]:
                names.append(i)

            for i in mcn[st:sp]:
                names.append(i)

            for i in csr[st:sp]:
                roll.append(i)

            for i in eer[st:sp]:
                roll.append(i)

            for i in cvr[st:sp]:
                roll.append(i)

            for i in mcr[st:sp]:
                roll.append(i)

        col1 = []
        col2 = []
        col3 = []

        print(len(names), len(roll), len(bench))

        for i in range(int(len(bench) / 25)):
            st = 25 * i
            sp = 25 * (i + 1)
            for a, b, c in zip(bench[st:sp], roll[st:sp], names[st:sp]):
                col1.append(a)
                col2.append(b)
                col3.append(c)

            dict = {'Invigilator': LecturerList[i], 'Bench_num': col1, 'Roll_num': col2, 'Student_name': col3}
            df = pd.DataFrame(dict)
            # Save result CSVs back to the 'static/uploads' folder
            df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'Room_{}.csv'.format(i + 1)))
            num = int(len(bench))

        return render_template('adminlog.html', Bench_num=bench, Roll_num=roll, Student_name=names, Num=num, LecturerList=LecturerList)

    return render_template('adminlog.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
