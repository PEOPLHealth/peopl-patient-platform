import os
import dotenv
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title='PEOPL',
    page_icon=':hospital:',
    layout="wide"
)

# Carga de variables de entorno
dotenv.load_dotenv()
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

BASE_ID_MONITOREO = "appNKQ1erVzjQOUTa"
BASE_ID_CALENDAR = "appmNRF046SxzA2cy"
BASE_ID_JUNTAS = "appKFWzkcDEWlrXBE"


TABLE_NAME_PRECONSULTA = "forms_pre-consulta"
TABLE_NAME_CPLATFORM = "calendar_platform"
TABLE_NAME_RECORDINGS = "contacto@peopl.health"
TABLE_NAME_JUNTAS = "Attendees SesionesC"


HEADERS = {"Authorization": f"Bearer {AIRTABLE_API_KEY}", "Content-Type": "application/json"}

# Función para cargar datos desde Airtable
def load_data(BASE_ID, TABLE_NAME, view=None):
    try:
        AIRTABLE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
        records = []
        params = {'view': view} if view else {}  # Include view in params if provided
        response = requests.get(AIRTABLE_URL, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()
        records.extend(data.get('records', []))

        while 'offset' in data:
            response = requests.get(AIRTABLE_URL, headers=HEADERS, params={'offset': data['offset']})
            response.raise_for_status()
            data = response.json()
            records.extend(data.get('records', []))

        if records:
            df = pd.DataFrame([record['fields'] for record in records])
            if "Created" in df.columns:
                df['Created'] = pd.to_datetime(df['Created'], errors='coerce')
            return df
        else:
            st.error("No se encontraron registros en Airtable.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()


# Cargar datos al inicio
data_monitoreo = load_data(BASE_ID_MONITOREO,TABLE_NAME_PRECONSULTA)
data_calendar = load_data(BASE_ID_CALENDAR,TABLE_NAME_CPLATFORM, view="streamlit - individual")
data_recording = load_data(BASE_ID_CALENDAR,TABLE_NAME_RECORDINGS,view="Yoga&Meditacion")
data_juntas = load_data(BASE_ID_JUNTAS,TABLE_NAME_JUNTAS,view="streamlit")

data_monitoreo['recordID_str']=data_monitoreo['patient'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_monitoreo['first_name_str']=data_monitoreo['first_name'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_monitoreo['specialties_str']=data_monitoreo['specialties'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_monitoreo['full_prescription']=data_monitoreo['full_prescription (from prescriptions)'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))


data_calendar['recordID_str']=data_calendar['recordID_patient'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_calendar['specialties_str']=data_calendar['specialty_id'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))

data_juntas['recordID_str']=data_juntas['recordID (from full_name)'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))


# Captura el parámetro recordID desde la URL
params = st.query_params
record_id = params.get('recordID', [None])  # Obtiene el recordID desde la URL

# record_id = "recjWwhBSgkzXmZo0"

# Validar si hay datos disponibles
if data_monitoreo.empty:
    st.warning("No hay datos disponibles en este momento.")
else:
    # Filtrar datos del paciente seleccionado
    patient_data = data_monitoreo[data_monitoreo['recordID_str'] == record_id]
    patient_data_calendar = data_calendar[data_calendar['recordID_str'] == record_id]
    patient_data_juntas = data_juntas[data_juntas['recordID_str'] == record_id]
    #st.dataframe(patient_data_calendar)

    recording_calendar_meditacion = data_recording[data_recording['Title'] == '[PEOPL] – Taller de meditación']
    recording_calendar_yoga = data_recording[data_recording['Title'] == '[PEOPL] -Taller de yoga']

    name = patient_data['first_name_str']

    st.title("🏥 PEOPL")
    st.write(f"Bienvenid@ {name.values[0]} a tu plataforma de seguimiento.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎥 Grabación de talleres","🥙 Nutrición", "🏃🏻 Rehabilitación", "👩🏻‍⚕ Medicina Paliativa", "🧠 Psicooncología"])

    nutri_record_id = 'rec9nx9loAzt8nWgn'
    rehab_record_id = 'recT9fqaCSFmAdYQZ'
    medpal_record_id = 'recjKw25D97FDYw0v'
    psico_record_id = 'recPIFlJuQIuYVjnK'

    nutri_record_id_calendar = 'recIqyN71LSHR94zL'
    rehab_record_id_calendar = 'recscg4Wf3YAjZ69n'
    medpal_record_id_calendar = 'recSNxGRgkqTmKEjT'
    psico_record_id_calendar = 'recIqyN71LSHR94zL'

    if patient_data.empty:
        st.warning("No se encontraron registros para este paciente.")
    else:
        with tab2:

            nu_tab1, nu_tab2, nutab3 = st.tabs(["🩺 Indicaciones", "📝 Resumen de la cita", "📄 Documentos"])
            
            patient_nutri_data = patient_data[patient_data['specialties_str']==nutri_record_id]

            
            with nu_tab1:

                selected_nutri_columns_ind = ['last_modified_general_indications','general_indications']
                nutri_filtered_data_ind = patient_nutri_data[selected_nutri_columns_ind]

                nutri_filtered_data_ind = nutri_filtered_data_ind[
                        (nutri_filtered_data_ind['general_indications'] != '') & (nutri_filtered_data_ind['general_indications'].notna())
                    ]

                nutri_filtered_data_ind['last_modified_general_indications'] = pd.to_datetime(nutri_filtered_data_ind['last_modified_general_indications']).dt.strftime('%d-%b-%Y')

                nutri_filtered_data_ind.columns = ['Fecha', 'Indicaciones']  # Change to your desired names 
                nutri_filtered_data_ind['Indicaciones'] = nutri_filtered_data_ind['Indicaciones'].str.replace('\n', '<br>', regex=False)
                nutri_table = nutri_filtered_data_ind.to_html(escape=False, index=False)

                # Reset the index to avoid displaying it
                st.markdown(nutri_table, unsafe_allow_html=True)
                
            with nu_tab2:

                # patient_nutri_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']]
                patient_nutri_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']==nutri_record_id_calendar]
                selected_nutri_columns = ['Start','recommendations']
                nutri_filtered_data_calendar = patient_nutri_data_calendar[selected_nutri_columns]
                nutri_filtered_data_calendar = nutri_filtered_data_calendar[
                        (nutri_filtered_data_calendar['recommendations'] != '') & (nutri_filtered_data_calendar['recommendations'].notna())
                    ]

                nutri_filtered_data_calendar['Start'] = pd.to_datetime(nutri_filtered_data_calendar['Start']).dt.date
                
                nutri_filtered_data_calendar['Start'] = pd.to_datetime(nutri_filtered_data_calendar['Start']).dt.strftime('%d-%b-%Y')

                nutri_filtered_data_calendar.columns = ['Fecha', 'Resumen de cita']  # Change to your desired names 
                nutri_filtered_data_calendar['Resumen de cita'] = nutri_filtered_data_calendar['Resumen de cita'].str.replace('\n', '<br>', regex=False)
                nutri_table_cal = nutri_filtered_data_calendar.to_html(escape=False, index=False)

                # Reset the index to avoid displaying it
                st.markdown(nutri_table_cal, unsafe_allow_html=True)
            
            with nutab3:

                selected_nutri_columns_file = ['manual_name','file_nutri_manuals']
                nutri_filtered_data_file = patient_nutri_data[selected_nutri_columns_file]

                nutri_filtered_data_file = nutri_filtered_data_file[
                        (nutri_filtered_data_file['file_nutri_manuals'] != '') & (nutri_filtered_data_file['file_nutri_manuals'].notna())
                    ]
                
                # Display files in Streamlit
                if not nutri_filtered_data_file.empty:
                    st.write("Archivos disponibles:")
                    for index, row in nutri_filtered_data_file.iterrows():
                        file_names = row['manual_name']  # Split the names
                        file_urls = row['file_nutri_manuals']  # Directly access the file URL
                        if isinstance(file_urls, list):  # Check if file_urls is a list
                            for file_name, file_url in zip(file_names, file_urls):
                                if file_url:  # Check if the URL is not empty
                                    st.markdown(f"[Descargar archivo: {file_name.strip()}]({file_url['url']})")  # Create a clickable link
                        else:
                            if file_urls:  # Check if the URL is not empty
                                st.markdown(f"[Descargar archivo: {file_names[0].strip()}]({file_urls['url']})")  


        with tab3:

            rehab_tab1, rehab_tab2, rehab_tab3 = st.tabs(["🩺 Indicaciones", "📝 Resumen de la cita", "📄 Documentos"])
            patient_rehab_data = patient_data[patient_data['specialties_str']==rehab_record_id]

            with rehab_tab1:
                selected_rehab_columns = ['last_modified_general_indications','general_indications']
                rehab_filtered_data = patient_rehab_data[selected_rehab_columns]

                rehab_filtered_data = rehab_filtered_data[
                        (rehab_filtered_data['general_indications'] != '') & (rehab_filtered_data['general_indications'].notna())
                    ]

                rehab_filtered_data['last_modified_general_indications'] = pd.to_datetime(rehab_filtered_data['last_modified_general_indications']).dt.strftime('%d-%b-%Y')
                

                rehab_filtered_data.columns = ['Fecha', 'Indicaciones']  # Change to your desired names 
                rehab_filtered_data['Indicaciones'] = rehab_filtered_data['Indicaciones'].str.replace('\n', '<br>', regex=False)
                rehab_table = rehab_filtered_data.to_html(escape=False, index=False)

                # Reset the index to avoid displaying it
                st.markdown(rehab_table, unsafe_allow_html=True)

            with rehab_tab2:

                # patient_nutri_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']]
                patient_rehab_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']==rehab_record_id_calendar]
                selected_rehab_columns = ['Start','recommendations']
                rehab_filtered_data_calendar = patient_rehab_data_calendar[selected_rehab_columns]
                rehab_filtered_data_calendar = rehab_filtered_data_calendar[
                        (rehab_filtered_data_calendar['recommendations'] != '') & (rehab_filtered_data_calendar['recommendations'].notna())
                    ]

                rehab_filtered_data_calendar['Start'] = pd.to_datetime(rehab_filtered_data_calendar['Start']).dt.strftime('%d-%b-%Y')
                

                rehab_filtered_data_calendar.columns = ['Fecha', 'Resumen de cita']  # Change to your desired names 
                rehab_filtered_data_calendar['Resumen de cita'] = rehab_filtered_data_calendar['Resumen de cita'].str.replace('\n', '<br>', regex=False)
                rehab_table_cal = rehab_filtered_data_calendar.to_html(escape=False, index=False)

                # Reset the index to avoid displaying it
                st.markdown(rehab_table_cal, unsafe_allow_html=True)
                
            with rehab_tab3:

                selected_rehab_columns_file = ['name_rehab_manuals','file_rehab_manuals']
                rehab_filtered_data_file = patient_rehab_data[selected_rehab_columns_file]

                rehab_filtered_data_file = rehab_filtered_data_file[
                        (rehab_filtered_data_file['file_rehab_manuals'] != '') & (rehab_filtered_data_file['file_rehab_manuals'].notna())
                    ]
                
                # Display files in Streamlit
                if not rehab_filtered_data_file.empty:
                    st.write("Archivos disponibles:")
                    for index, row in rehab_filtered_data_file.iterrows():
                        file_names = row['name_rehab_manuals']  # Split the names
                        file_urls = row['file_rehab_manuals']  # Directly access the file URL
                        if isinstance(file_urls, list):  # Check if file_urls is a list
                            for file_name, file_url in zip(file_names, file_urls):
                                if file_url:  # Check if the URL is not empty
                                    st.markdown(f"[Descargar archivo: {file_name.strip()}]({file_url['url']})")  # Create a clickable link
                        else:
                            if file_urls:  # Check if the URL is not empty
                                st.markdown(f"[Descargar archivo: {file_names[0].strip()}]({file_urls['url']})")  


        with tab4:
            medpal_tab1, medpal_tab2, medpal_tab3 = st.tabs(["🩺 Indicaciones", "📝 Resumen de la cita", "📄 Receta"])
            patient_medpal_data = patient_data[patient_data['specialties_str']==medpal_record_id]

            with medpal_tab1:
                selected_medpal_columns = ['real_date','full_prescription']
                medpal_filtered_data = patient_medpal_data[selected_medpal_columns]

                medpal_filtered_data = medpal_filtered_data[
                        (medpal_filtered_data['full_prescription'] != '') & (medpal_filtered_data['full_prescription'].notna())
                    ]

                medpal_filtered_data['real_date'] = pd.to_datetime(medpal_filtered_data['real_date']).dt.strftime('%d-%b-%Y')
                

                medpal_filtered_data.columns = ['Fecha', 'Indicaciones']  # Change to your desired names 
                medpal_filtered_data['Indicaciones'] = medpal_filtered_data['Indicaciones'].str.replace('\n', '<br>', regex=False)
                medpal_table = medpal_filtered_data.to_html(escape=False, index=False)

                # Reset the index to avoid displaying it
                st.markdown(medpal_table, unsafe_allow_html=True)

            with medpal_tab2:

                # patient_nutri_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']]
                patient_medpal_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']==medpal_record_id_calendar]
                selected_medpal_columns = ['Start','recommendations']
                medpal_filtered_data_calendar = patient_medpal_data_calendar[selected_medpal_columns]
                medpal_filtered_data_calendar = medpal_filtered_data_calendar[
                        (medpal_filtered_data_calendar['recommendations'] != '') & (medpal_filtered_data_calendar['recommendations'].notna())
                    ]

                medpal_filtered_data_calendar['Start'] = pd.to_datetime(medpal_filtered_data_calendar['Start']).dt.strftime('%d-%b-%Y')
                

                medpal_filtered_data_calendar.columns = ['Fecha', 'Resumen de cita']  # Change to your desired names 
                medpal_filtered_data_calendar['Resumen de cita'] = medpal_filtered_data_calendar['Resumen de cita'].str.replace('\n', '<br>', regex=False)
                medpal_table_cal = medpal_filtered_data_calendar.to_html(escape=False, index=False)

                # Reset the index to avoid displaying it
                st.markdown(medpal_table_cal, unsafe_allow_html=True)
                
            with medpal_tab3:

                selected_medpal_columns_file = ['real_date','doc_receta']
                medpal_filtered_data_file = patient_medpal_data[selected_medpal_columns_file]

                medpal_filtered_data_file = medpal_filtered_data_file[
                        (medpal_filtered_data_file['doc_receta'] != '') & (medpal_filtered_data_file['doc_receta'].notna())
                    ]
                
                # Display files in Streamlit
                if not medpal_filtered_data_file.empty:
                    st.write("Archivos disponibles:")
                    for index, row in medpal_filtered_data_file.iterrows():
                        file_dates = row['real_date']  # Split the names
                        file_urls = row['doc_receta']  # Directly access the file URL
                        for file_date, file_url in zip(file_dates, file_urls):
                                st.markdown(f"[Descargar receta médica: {file_dates}]({file_url['url']})")  # Create a clickable link


        with tab1:

            option = st.selectbox("Elige el taller:", ["Yoga 🧘‍♀️", "Meditación 🧘‍♀️"])
            if option == "Yoga 🧘‍♀️":
                st.write('Disfruta de las sesiones de yoga 🧘‍♀️')
                yoga_filtered = recording_calendar_yoga[
                    (recording_calendar_yoga['url_recording'] != '') & (recording_calendar_yoga['url_recording'].notna())
                ]
                selected_yoga_columns = ['Start','url_recording']
                yoga_filtered = yoga_filtered[selected_yoga_columns]

                yoga_filtered['Start'] = pd.to_datetime(yoga_filtered['Start']).dt.tz_convert('America/Mexico_City').dt.date
                yoga_filtered = yoga_filtered.sort_values(by='Start', ascending=False)  # Sort by Start date descending

                st.dataframe(
                    yoga_filtered, 
                    column_config = {
                        "Start": "Fecha de taller",
                        "url_recording": st.column_config.LinkColumn("Liga de sesión")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.write('Disfruta de las sesiones de meditación 🧘‍♀️')
                meditacion_filtered = recording_calendar_meditacion[
                    (recording_calendar_meditacion['url_recording'] != '') & (recording_calendar_meditacion['url_recording'].notna())
                ]
                selected_meditacion_columns = ['Start','url_recording']
                meditacion_filtered = meditacion_filtered[selected_meditacion_columns]

                meditacion_filtered['Start'] = pd.to_datetime(meditacion_filtered['Start']).dt.tz_convert('America/Mexico_City').dt.date
                meditacion_filtered = meditacion_filtered.sort_values(by='Start', ascending=False)  # Sort by Start date descending

                st.dataframe(
                    meditacion_filtered, 
                    column_config = {
                        "Start": "Fecha de taller",
                        "url_recording": st.column_config.LinkColumn("Liga de sesión")
                    },
                    use_container_width=True,
                    hide_index=True
                )
