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
TABLE_NAME_PRECONSULTA = "forms_pre-consulta"
BASE_ID_CALENDAR = "appmNRF046SxzA2cy"
TABLE_NAME_CPLATFORM = "calendar_platform"
TABLE_NAME_RECORDINGS = "contacto@peopl.health"


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


data_monitoreo['recordID_str']=data_monitoreo['patient'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_monitoreo['specialties_str']=data_monitoreo['specialties'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))

data_calendar['recordID_str']=data_calendar['recordID_patient'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))
data_calendar['specialties_str']=data_calendar['specialty_id'].apply(lambda x: str(x[0]) if isinstance(x, list) and len(x) > 0 else str(x))

# Captura el parámetro recordID desde la URL
params = st.query_params
record_id = params.get('recordID', [None])  # Obtiene el recordID desde la URL

# record_id = "recWu820ocWN0ylPN"

# Validar si hay datos disponibles
if data_monitoreo.empty:
    st.warning("No hay datos disponibles en este momento.")
else:
    # Filtrar datos del paciente seleccionado
    patient_data = data_monitoreo[data_monitoreo['recordID_str'] == record_id]
    patient_data_calendar = data_calendar[data_calendar['recordID_str'] == record_id]
    st.dataframe(patient_data_calendar)

    recording_calendar_meditacion = data_recording[data_recording['Title'] == '[PEOPL] – Taller de meditación']
    recording_calendar_yoga = data_recording[data_recording['Title'] == '[PEOPL] -Taller de yoga']

    name = patient_data['first_name'].iloc[0]

    st.title("🏥 PEOPL")
    st.write(f"Bienvenid@ {name[0]} a tu plataforma de seguimiento.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Nutrición", "Rehabilitación", "Medicina Paliativa", "Psicooncología", "🎥 Grabación de talleres"])

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
        with tab1:
            st.write("Indicaciones")
            patient_nutri_data = patient_data[patient_data['specialties_str']==nutri_record_id]
            selected_nutri_columns = ['last_modified_general_indications','general_indications']
            nutri_filtered_data = patient_nutri_data[selected_nutri_columns]
            nutri_filtered_data = nutri_filtered_data[
                    (nutri_filtered_data['general_indications'] != '') & (nutri_filtered_data['general_indications'].notna())
                ]

            nutri_filtered_data['last_modified_general_indications'] = pd.to_datetime(nutri_filtered_data['last_modified_general_indications']).dt.strftime('%d-%b-%Y')
            
            #nd = pd.DataFrame(
            #    nutri_filtered_data,
            #    column_config = {
            #            "last_modified_general_indications": "Fecha de cita",
            #            "general_indications": "Indicaciones de la cita"
            #        }, 
            #    use_container_width=True,
            #    hide_index=True
            #    )


            nutri_filtered_data.columns = ['Fecha', 'Indicaciones']  # Change to your desired names 
            nutri_filtered_data['Indicaciones'] = nutri_filtered_data['Indicaciones'].str.replace('\n', '<br>', regex=False)
            nutri_table = nutri_filtered_data.to_html(escape=False, index=False)

            # Reset the index to avoid displaying it
            st.markdown(nutri_table, unsafe_allow_html=True)
        


            st.write('Resumen de cita')
            # patient_nutri_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']]
            patient_nutri_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']==nutri_record_id_calendar]
            selected_nutri_columns = ['Start','recommendations']
            nutri_filtered_data_calendar = patient_nutri_data_calendar[selected_nutri_columns]
            nutri_filtered_data_calendar = nutri_filtered_data_calendar[
                    (nutri_filtered_data_calendar['recommendations'] != '') & (nutri_filtered_data_calendar['recommendations'].notna())
                ]

            nutri_filtered_data_calendar['Start'] = pd.to_datetime(nutri_filtered_data_calendar['Start']).dt.date
            
            st.dataframe(
                nutri_filtered_data_calendar,
                column_config = {
                        "Start": "Fecha de cita",
                        "recommendations": "Resumen de la cita"
                    }, 
                use_container_width=True,
                hide_index=True
                )

        with tab2:
            st.write("Indicaciones")
            patient_rehab_data = patient_data[patient_data['specialties_str']==rehab_record_id]
            selected_rehab_columns = ['last_modified_general_indications','general_indications']
            rehab_filtered_data = patient_rehab_data[selected_rehab_columns]
            rehab_filtered_data = rehab_filtered_data[
                    (rehab_filtered_data['general_indications'] != '') & (rehab_filtered_data['general_indications'].notna())
                ]

            rehab_filtered_data['last_modified_general_indications'] = pd.to_datetime(rehab_filtered_data['last_modified_general_indications']).dt.date
            
            st.dataframe(
                rehab_filtered_data,
                column_config = {
                        "last_modified_general_indications": "Fecha de cita",
                        "general_indications": "Resumen de la cita"
                    },
                use_container_width=True,
                hide_index=True
            )


            st.write('Resumen de cita')
            # patient_nutri_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']]
            patient_rehab_data_calendar = patient_data_calendar[patient_data_calendar['specialties_str']==rehab_record_id_calendar]
            selected_rehab_columns = ['Start','recommendations']
            rehab_filtered_data_calendar = patient_rehab_data_calendar[selected_rehab_columns]
            rehab_filtered_data_calendar = rehab_filtered_data_calendar[
                    (rehab_filtered_data_calendar['recommendations'] != '') & (rehab_filtered_data_calendar['recommendations'].notna())
                ]

            rehab_filtered_data_calendar['Start'] = pd.to_datetime(rehab_filtered_data_calendar['Start']).dt.date
            
            st.dataframe(
                rehab_filtered_data_calendar,
                column_config = {
                        "Start": "Fecha de cita",
                        "recommendations": "Resumen de la cita"
                    },
                use_container_width=True,
                hide_index=True
            )

        with tab3:
            st.write("Contenido de Progreso General")

        with tab5:

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



