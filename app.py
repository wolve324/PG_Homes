import pandas as pd
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, request, redirect, url_for, flash, render_template, jsonify
import logging
import requests
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template
from enquiry import enquiry_bp
from upload_app import upload_bp


UPLOAD_URL = "https://pghomes.pythonanywhere.com/upload"

app = Flask(__name__, static_folder='static', template_folder='templates')
app.register_blueprint(enquiry_bp)
app.register_blueprint(upload_bp)
app.secret_key = 'supersecretkey'

def upload_file(file_path):
    files = {"file": open(file_path, "rb")}
    response = requests.post(UPLOAD_URL, files=files)
    return response.json()

@app.route('/')
def home():
    return render_template('index.html')


def format_date(date):
    """Format date as 'yyyy-MM-dd'. Return an empty string if the date is None."""
    if pd.isna(date):
        return None
    if isinstance(date, pd.Timestamp):
        return date.strftime('%Y-%m-%d')
    return date



@app.route('/submit', methods=['POST'])
def submit():
    try:
        file1 = request.files.get('Aadhar')
        file2 = request.files.get('Company')
        filename1 = filename2 = None

        if file1 and allowed_file(file1.filename):
            filename1 = secure_filename(file1.filename)
            file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            app.logger.info(f"File1 saved: {filename1}")

        if file2 and allowed_file(file2.filename):
            filename2 = secure_filename(file2.filename)
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
            app.logger.info(f"File2 saved: {filename2}")

        data = {
            'LOCATION': request.form.get('Area', ''),
            'PROPERTY': request.form.get('Property_selected', ''),
            'BED ID': request.form.get('bedId', ''),
            'NAME': request.form.get('name', ''),
            'TYPE': request.form.get('type', ''),
            'CONTACT': request.form.get('mobileNumber', ''),
            'RENT': request.form.get('rent', ''),
            'DEPOSIT': request.form.get('deposit', ''),
            'JOINING_DATE': request.form.get('joiningDate', ''),
            'RD': request.form.get('rd', ''),
            'STATUS': request.form.get('paidStatus', ''),
            'PAID_TO': request.form.get('paidTo', ''),
            'DATE OF PAYMENT': request.form.get('dateOfPayment', ''),

        }
        app.logger.info(f"Form data received: {data}")

        # Load or create DataFrames for NewData and OldData
        if os.path.exists(EXCEL_FILE):
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                try:
                    new_df = pd.read_excel(EXCEL_FILE, sheet_name='NewData')
                except ValueError:
                    new_df = pd.DataFrame(columns=data.keys())
                    app.logger.info(f"NewData sheet not found, created new DataFrame with columns: {data.keys()}")
                try:
                    old_df = pd.read_excel(EXCEL_FILE, sheet_name='OldData')
                except ValueError:
                    old_df = pd.DataFrame(columns=data.keys())
                    app.logger.info(f"OldData sheet not found, created new DataFrame with columns: {data.keys()}")

                # Append new data to NewData sheet
                new_df = new_df.append(data, ignore_index=True)
                new_df.to_excel(writer, sheet_name='NewData', index=False)

                # Save old data to OldData sheet
                old_df.to_excel(writer, sheet_name='OldData', index=False)
                app.logger.info(f"Excel file saved at {EXCEL_FILE}")
        else:
            new_df = pd.DataFrame(columns=data.keys())
            old_df = pd.DataFrame(columns=data.keys())
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
                new_df.to_excel(writer, sheet_name='NewData', index=False)
                old_df.to_excel(writer, sheet_name='OldData', index=False)
                app.logger.info(f"Excel file not found, created new Excel file with NewData and OldData sheets")

        flash('Form submitted successfully!')
    except Exception as e:
        flash(f'An error occurred: {e}')
        app.logger.error(f"Error: {e}")

    return redirect(url_for('home'))
@app.route('/submit_documents', methods=['POST'])
def submit_documents():
    try:
        file1 = request.files.get('document1')  # Change to your input field name
        file2 = request.files.get('document2')  # Change to your input field name
        filename1 = filename2 = None

        if file1 and allowed_file(file1.filename):
            filename1 = secure_filename(file1.filename)
            file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            app.logger.info(f"Document1 saved: {filename1}")

        if file2 and allowed_file(file2.filename):
            filename2 = secure_filename(file2.filename)
            file2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
            app.logger.info(f"Document2 saved: {filename2}")

        flash('Documents submitted successfully!')
    except Exception as e:
        flash(f'An error occurred while submitting documents: {e}')
        app.logger.error(f"Error: {e}")

    return redirect(url_for('home'))


def normalize_column_names(df):
    df.columns = [col.strip().upper().replace(' ', '_') for col in df.columns]
    return df


@app.route('/api/get_data', methods=['GET'])
def get_data():
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name='OldData')

        app.logger.info("DataFrame loaded:")
        app.logger.info(df.head())
        app.logger.info("Columns in DataFrame: %s", df.columns.tolist())

        # Retrieve query parameters
        location = request.args.get('location', '').strip().upper()
        property_ = request.args.get('property', '').strip().upper()
        status = request.args.get('status', '').strip().upper()

        app.logger.info(f"Received query parameters: location={location}, property={property_}, status={status}")

        # Normalize data by stripping whitespace and converting to uppercase
        df['LOCATION'] = df['LOCATION'].str.strip().str.upper()
        df['PROPERTY'] = df['PROPERTY'].str.strip().str.upper()
        df['STATUS'] = df['STATUS'].str.strip().str.upper()

        # Apply filters based on query parameters
        if location:
            df = df[df['LOCATION'] == location]
        if property_:
            df = df[df['PROPERTY'] == property_]
        if status:
            df = df[df['STATUS'] == status]


        df['DATE OF PAYMENT'] = df['DATE OF PAYMENT'].apply(format_date)

        # Replace NaN values with None (null in JSON)
        df = df.applymap(lambda x: None if pd.isna(x) else x)

        # Convert DataFrame to JSON
        data = df.to_dict(orient='records')
        app.logger.info(f"Filtered data: {data}")

        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error fetching data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_data', methods=['POST'])
def update_data():
    try:
        updated_data = request.json
        df = pd.read_excel(EXCEL_FILE, sheet_name='NewData')

        for entry in updated_data:
            index = df.index[df['BED ID'] == entry['BED ID']].tolist()
            if index:
                for key, value in entry.items():
                    df.at[index[0], key] = value

        df.to_excel(EXCEL_FILE, sheet_name='NewData', index=False)
        return jsonify({'status': 'success'})
    except Exception as e:
        app.logger.error(f"Error updating data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # You can choose any available port