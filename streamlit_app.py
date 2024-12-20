import os
import dotenv
import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title='Plataforma PEOPL',
    page_icon='https://i.postimg.cc/tRvZtXHB/logo-1.png',
    layout="wide"
)
st.markdown(
    """
    <style>
    .top-right {
        position: absolute;
        top: 3px;
        right: 10px;
    }
    </style>
    <div class="top-right">
        <img src="https://i.postimg.cc/tRvZtXHB/logo-1.png" width="150">
    </div>
    """,
    unsafe_allow_html=True
)    
# Carga de variables de entorno
dotenv.load_dotenv()
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")

BASE_ID_MONITOREO = "appNKQ1erVzjQOUTa"
BASE_ID_CALENDAR = "appmNRF046SxzA2cy"
BASE_ID_JUNTAS = "appKFWzkcDEWlrXBE"

TABLE_NAME_ESTADO_GENERAL = "estado_general"
TABLE_NAME_PRECONSULTA = "forms_pre-consulta"
TABLE_NAME_CPLATFORM = "calendar_platform"
TABLE_NAME_RECOMMENDATIONS = "recommendations"
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
data_estado_general = load_data(BASE_ID_MONITOREO,TABLE_NAME_ESTADO_GENERAL,view="streamlit")
data_monitoreo = load_data(BASE_ID_MONITOREO,TABLE_NAME_PRECONSULTA)
data_calendar = load_data(BASE_ID_CALENDAR,TABLE_NAME_RECOMMENDATIONS)
data_calendar_ns = load_data(BASE_ID_CALENDAR,TABLE_NAME_CPLATFORM, view="streamlit - next sessions")
data_recording = load_data(BASE_ID_CALENDAR,TABLE_NAME_RECORDINGS,view="Yoga&Meditacion")
data_juntas = load_data(BASE_ID_JUNTAS,TABLE_NAME_JUNTAS,view="streamlit")

data_monitoreo['recordID_str']=data_monitoreo['patient'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_monitoreo['specialties_str']=data_monitoreo['specialties'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_monitoreo['full_prescription']=data_monitoreo['full_prescription (from prescriptions)'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))


data_calendar['recordID_str']=data_calendar['recordID_patient'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_calendar['specialties_str']=data_calendar['specialty_id'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_calendar['start_str']=data_calendar['start'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))

data_juntas['recordID_str']=data_juntas['recordID (from full_name)'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_juntas['specialty_str']=data_juntas['specialty_id'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))

data_estado_general['recordID_str']=data_estado_general['recordID_patient'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_estado_general['first_name_str']=data_estado_general['first_name'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))

data_calendar_ns['recordID_str'] = data_calendar_ns['recordID_patient'].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) and len(x) > 0 else str(x))

# Captura el parámetro recordID desde la URL
params = st.query_params
record_id = params.get('recordID', [None])  # Obtiene el recordID desde la URL

# Validar si hay datos disponibles
if data_estado_general.empty:
    st.warning("No hay datos disponibles en este momento.")
else:
    # Filtrar datos del paciente seleccionado
    patient_data = data_monitoreo[data_monitoreo['recordID_str'] == record_id]
    patient_data_calendar = data_calendar[data_calendar['recordID_str'] == record_id]
    patient_data_calendar_ns = data_calendar_ns[data_calendar_ns['recordID_str'].str.contains(record_id, na=False)]
    patient_data_juntas = data_juntas[data_juntas['recordID_str'] == record_id]
    patient_data_eg = data_estado_general[data_estado_general['recordID_str'] == record_id]
    #st.dataframe(patient_data_calendar)

    recording_calendar_meditacion = data_recording[data_recording['Title'] == '[PEOPL] – Taller de meditación']
    recording_calendar_yoga = data_recording[data_recording['Title'] == '[PEOPL] -Taller de yoga']

    name = patient_data_eg['first_name_str']
    name = name.iloc[0]

    st.markdown(
        f"""
        <div style="display: flex; align-items: center;">
            <div style="margin-right: 10px;">  <!-- Espacio entre la imagen y la burbuja -->
                <img src="https://i.ibb.co/LJ1GZPh/Disen-o-sin-ti-tulo-4.png" width="100">
            </div>
            <div class="message-bubble" style="display: inline-block; padding: 10px; margin: 10px; border-radius: 15px; background-color: #f0f0f0; border: 1px solid #ccc; max-width: 300px; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1); color: black;">
                Bienvenid@ {name} a tu plataforma de seguimiento 😊
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write('')
    link = 'https://patient-indicators.streamlit.app/?recordID='+record_id
    st.write("Para visualizar tus indicadores clínicos revisa en la siguiente liga:",f"[Indicadores Clínicos 📊]({link})")


    tabp, tab1, tab2, tab3, tab4, tab5 = st.tabs(["Resumen", "🎥 Grabación de talleres","🥙 Nutrición", "🏃🏻 Rehabilitación", "👩🏻‍⚕ Medicina Paliativa", "🧠 Psicooncología"])

    nutri_record_id = 'rec9nx9loAzt8nWgn'
    rehab_record_id = 'recT9fqaCSFmAdYQZ'
    medpal_record_id = 'recjKw25D97FDYw0v'
    psico_record_id = 'recPIFlJuQIuYVjnK'

    nutri_record_id_calendar = 'recIqyN71LSHR94zL'
    rehab_record_id_calendar = 'recscg4Wf3YAjZ69n'
    medpal_record_id_calendar = 'recSNxGRgkqTmKEjT'
    psico_record_id_calendar = 'recIqyN71LSHR94zL'

    if patient_data_eg.empty:
        st.warning("No se encontraron registros para este paciente.")
    else:
        with tabp:
            program = patient_data_eg['Program'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
            due_date = patient_data_eg['next_due_date']
            days_to_due_date = patient_data_eg['days_to_due_date']
            st.write(f'Tienes activo el plan **{program.iloc[0]}** 💙. Con este programa, cada mes tienes acceso a:')

            if (program.iloc[0]=='Vive Bien'):
                st.write('* 👩🏻‍⚕️ 2 citas individuales')
                st.markdown("""
                - 👥 Sesiones colectivas y talleres ilimitados
                    - Sesiones colectivas de nutrición, rehabilitación, psicooncología, etc.
                    - Talleres:
                        - 🧘‍♂️ **Meditación**: Cada **lunes** a las 🕣 **8:30 PM**.
                        - 🧘‍♀️ **Yoga**: Cada **viernes** a las 🕗 **8:00 PM**.
                """)

            elif (program.iloc[0]=='Juntas'):
                st.markdown("""
                - 👥 Sesiones colectivas y talleres ilimitados
                    - Sesiones colectivas de nutrición, rehabilitación, psicooncología, etc.
                    - Talleres:
                        - 🧘‍♂️ **Meditación**: Cada **lunes** a las 🕣 **8:30 PM**.
                        - 🧘‍♀️ **Yoga**: Cada **viernes** a las 🕗 **8:00 PM**.
                """)
            elif (program.iloc[0]=='Contigo'):
                st.markdown("""
                - 👥 Sesiones colectivas quincenales y talleres semanales
                    - Sesiones colectivas de nutrición, rehabilitación, psicooncología, etc.
                    - Talleres:
                        - 🧘‍♂️ **Meditación**: Cada **lunes** a las 🕣 **8:30 PM**.
                        - 🧘‍♀️ **Yoga**: Cada **viernes** a las 🕗 **8:00 PM**.
                """)

            st.markdown("<hr>", unsafe_allow_html=True)

            st.markdown('#### Tus próximas sesiones 🗓️:')
            if patient_data_calendar_ns.empty:
                st.write("No hay futuras citas agendadas.")
            else:
                patient_data_calendar_ns.rename(columns={'title_streamlit': 'Cita médica', 'Start': 'Fecha y hora'}, inplace=True)  # Cambiar el nombre de la columna
                patient_data_calendar_ns['Fecha y hora'] = pd.to_datetime(patient_data_calendar_ns['Fecha y hora'])
                # Verificar si ya tiene información de zona horaria antes de aplicar tz_localize
                if patient_data_calendar_ns['Fecha y hora'].dt.tz is None:
                    patient_data_calendar_ns['Fecha y hora'] = patient_data_calendar_ns['Fecha y hora'].dt.tz_localize('UTC')
                patient_data_calendar_ns['Fecha y hora'] = patient_data_calendar_ns['Fecha y hora'].dt.tz_convert('America/Mexico_City').dt.strftime('%d/%m/%Y %H:%M')

                st.write(patient_data_calendar_ns[['Cita médica','Fecha y hora']])

            st.markdown("<hr>", unsafe_allow_html=True)

            st.write(f'**Fecha próxima de pago:** {due_date.iloc[0]}, en {days_to_due_date.iloc[0]} días')



        with tab2:

            nu_tab1, nu_tab2, nutab3 = st.tabs(["🩺 Indicaciones", "📝 Resumen de la cita", "📄 Documentos"])
            
            patient_nutri_data = patient_data[patient_data['specialties_str']==nutri_record_id]
            patient_nutri_juntas = patient_data_juntas[patient_data_juntas['specialty_str'] == nutri_record_id]

            
            with nu_tab1:

                selected_nutri_columns_ind = ['last_modified_general_indications','general_indications']
                selected_nutri_columns_ind_juntas = ['last_modified_ind','general_indications']

                nutri_filtered_data_ind = patient_nutri_data[selected_nutri_columns_ind]
                nutri_filtered_data_ind_juntas = patient_nutri_juntas[selected_nutri_columns_ind_juntas]

                nutri_filtered_data_ind.columns = ['Fecha', 'Indicaciones']
                nutri_filtered_data_ind_juntas.columns = ['Fecha', 'Indicaciones']

                nutri_filtered_data_ind = nutri_filtered_data_ind[
                        (nutri_filtered_data_ind['Indicaciones'] != '') & (nutri_filtered_data_ind['Indicaciones'].notna())
                    ]
                
                nutri_filtered_data_ind['Fecha'] = pd.to_datetime(nutri_filtered_data_ind['Fecha']).dt.strftime('%d-%b-%Y')
                nutri_filtered_data_ind_juntas['Fecha'] = pd.to_datetime(nutri_filtered_data_ind_juntas['Fecha']).dt.strftime('%d-%b-%Y')

                # Join the two DataFrames
                combined_nutri_data = pd.concat([nutri_filtered_data_ind, nutri_filtered_data_ind_juntas], ignore_index=True)


                combined_nutri_data.columns = ['Fecha', 'Indicaciones']  # Change to your desired names 
                combined_nutri_data['Indicaciones'] = combined_nutri_data['Indicaciones'].str.replace('\n', '<br>', regex=False)
                nutri_table = combined_nutri_data.to_html(escape=False, index=False)

                # Reset the index to avoid displaying it
                st.markdown(nutri_table, unsafe_allow_html=True)
                
            with nu_tab2:

                # patient_nutri_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']]
                patient_nutri_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']==nutri_record_id_calendar]
                selected_nutri_columns = ['start_str','recommendations']
                nutri_filtered_data_calendar = patient_nutri_data_calendar[selected_nutri_columns]
                nutri_filtered_data_calendar = nutri_filtered_data_calendar[
                        (nutri_filtered_data_calendar['recommendations'] != '') & (nutri_filtered_data_calendar['recommendations'].notna())
                    ]

                nutri_filtered_data_calendar['start_str'] = pd.to_datetime(nutri_filtered_data_calendar['start_str']).dt.date
                
                nutri_filtered_data_calendar['start_str'] = pd.to_datetime(nutri_filtered_data_calendar['start_str']).dt.strftime('%d-%b-%Y')

                nutri_filtered_data_calendar.columns = ['Fecha', 'Resumen de cita']  # Change to your desired names 
                nutri_filtered_data_calendar['Resumen de cita'] = nutri_filtered_data_calendar['Resumen de cita'].str.replace('\n', '<br>', regex=False)
                nutri_table_cal = nutri_filtered_data_calendar.to_html(escape=False, index=False)

                # Reset the index to avoid displaying it
                st.markdown(nutri_table_cal, unsafe_allow_html=True)
            
            with nutab3:

                selected_nutri_columns_file = ['manual_name','file_nutri_manuals']
                selected_nutri_columns_file_juntas = ['manual_name','file_nutri_manuals']

                nutri_filtered_data_file = patient_nutri_data[selected_nutri_columns_file]
                nutri_filtered_data_file_juntas = patient_nutri_juntas[selected_nutri_columns_file_juntas]

                nutri_filtered_data_file = nutri_filtered_data_file[
                        (nutri_filtered_data_file['file_nutri_manuals'] != '') & (nutri_filtered_data_file['file_nutri_manuals'].notna())
                    ]
                
                combined_nutri_data_files = pd.concat([nutri_filtered_data_file, nutri_filtered_data_file_juntas], ignore_index=True)

                # Display files in Streamlit
                if not combined_nutri_data_files.empty:
                    st.write("Archivos disponibles:")
                    for index, row in combined_nutri_data_files.iterrows():
                        file_names = row['manual_name']  # Split the names
                        file_urls = row['file_nutri_manuals']  # Directly access the file URL

                        # Check if file_urls is a list
                        if isinstance(file_urls, list):
                            for file_name, file_url in zip(file_names, file_urls):
                                if isinstance(file_url, dict) and 'url' in file_url:  # Check if file_url is a dict and has 'url'
                                    st.markdown(f"[Descargar archivo: {file_name.strip()}]({file_url['url']})")  # Create a clickable link
                        elif isinstance(file_urls, dict) and 'url' in file_urls:  # Check if file_urls is a dict
                            st.markdown(f"[Descargar archivo: {file_names.strip()}]({file_urls['url']})")  # Create a clickable link

                        #if isinstance(file_urls, list):  # Check if file_urls is a list
                        #    for file_name, file_url in zip(file_names, file_urls):
                        #        if file_url:  # Check if the URL is not empty
                        #            st.markdown(f"[Descargar archivo: {file_name.strip()}]({file_url['url']})")  # Create a clickable link
                        #else:
                        #    if file_urls:  # Check if the URL is not empty
                        #        st.markdown(f"[Descargar archivo: {file_names[0].strip()}]({file_urls['url']})")  


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
                selected_rehab_columns = ['start_str','recommendations']
                rehab_filtered_data_calendar = patient_rehab_data_calendar[selected_rehab_columns]
                rehab_filtered_data_calendar = rehab_filtered_data_calendar[
                        (rehab_filtered_data_calendar['recommendations'] != '') & (rehab_filtered_data_calendar['recommendations'].notna())
                    ]

                rehab_filtered_data_calendar['start_str'] = pd.to_datetime(rehab_filtered_data_calendar['start_str']).dt.strftime('%d-%b-%Y')
                

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
                selected_medpal_columns = ['start_str','recommendations']
                medpal_filtered_data_calendar = patient_medpal_data_calendar[selected_medpal_columns]
                medpal_filtered_data_calendar = medpal_filtered_data_calendar[
                        (medpal_filtered_data_calendar['recommendations'] != '') & (medpal_filtered_data_calendar['recommendations'].notna())
                    ]

                medpal_filtered_data_calendar['start_str'] = pd.to_datetime(medpal_filtered_data_calendar['start_str']).dt.strftime('%d-%b-%Y')
                

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
