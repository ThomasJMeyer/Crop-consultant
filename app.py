import streamlit as st
import sqlite3, json, datetime, os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
DB='cropconsult.db'
con=sqlite3.connect(DB,check_same_thread=False)
con.execute('CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, created TEXT, grower TEXT, field TEXT, acres REAL, crop TEXT, stage TEXT, weeds TEXT, insects TEXT, diseases TEXT, moisture TEXT, observations TEXT, recommendations TEXT)')
con.commit()
st.set_page_config(page_title='CropConsult AI',page_icon='🌾',layout='wide')
st.title('🌾 CropConsult AI')
st.caption('Crop scouting • Grower reports • Field history')
with st.sidebar:
    st.header('Consulting business')
    business=st.text_input('Business name','CropConsult AI')
    st.info('AI drafting is optional. Set OPENAI_API_KEY in your environment to enable it. Always review agronomic recommendations before sharing.')
page=st.radio('Navigate',['New scouting report','Report history','Input calculator'])
def pdf_report(d):
    buf=BytesIO(); doc=SimpleDocTemplate(buf); styles=getSampleStyleSheet(); story=[Paragraph(business,styles['Title']),Paragraph('Crop Scouting Report',styles['Heading2']),Spacer(1,12)]
    for k,v in d.items():
        story.append(Paragraph(f'<b>{k}:</b> {str(v).replace("&","&amp;").replace("<","&lt;")}',styles['BodyText']));story.append(Spacer(1,8))
    story.append(Paragraph('Recommendations require consultant verification and compliance with current product labels.',styles['Italic']))
    doc.build(story);return buf.getvalue()
if page=='New scouting report':
    with st.form('scout'):
        a,b,c=st.columns(3)
        grower=a.text_input('Grower / customer *'); field=b.text_input('Field name *'); acres=c.number_input('Acres',min_value=0.0,value=125.0)
        crop=a.selectbox('Crop',['Corn','Wheat','Sorghum / Milo','Cotton','Canola','Other']);stage=b.text_input('Growth stage');moisture=c.selectbox('Moisture',['Adequate','Dry','Excess','Variable','Unknown'])
        weeds=st.text_area('Weeds observed');insects=st.text_area('Insects observed');diseases=st.text_area('Disease symptoms');observations=st.text_area('Scouting observations');recommendations=st.text_area('Consultant recommendations / action items')
        submit=st.form_submit_button('Save scouting report',type='primary')
    if submit:
        if not grower or not field:st.error('Enter a grower and field name.')
        else:
            con.execute('INSERT INTO reports (created,grower,field,acres,crop,stage,weeds,insects,diseases,moisture,observations,recommendations) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(str(datetime.date.today()),grower,field,acres,crop,stage,weeds,insects,diseases,moisture,observations,recommendations));con.commit();st.success('Report saved.')
    rows=con.execute('SELECT * FROM reports ORDER BY id DESC LIMIT 1').fetchall()
    if rows:
        cols=[x[1] for x in con.execute('PRAGMA table_info(reports)').fetchall()]; d=dict(zip(cols,rows[0]));d.pop('id',None)
        st.subheader('Latest report')
        st.json(d)
        st.download_button('Download PDF',pdf_report(d),file_name='crop_scouting_report.pdf',mime='application/pdf')
        if st.button('Generate AI draft from latest report'):
            try:
                from openai import OpenAI
                client=OpenAI()
                response=client.responses.create(model='gpt-4.1-mini',instructions='You draft concise, professional agronomic scouting reports. Do not invent observations, pest thresholds, product rates, diagnoses or label claims. Clearly distinguish observations from possible causes and recommended verification. Do not recommend pesticide products or application rates without confirmed local labels and context.',input=json.dumps(d))
                st.markdown(response.output_text)
            except Exception as e:st.warning('AI drafting unavailable. Configure OPENAI_API_KEY and install openai. '+str(e))
elif page=='Report history':
    rows=con.execute('SELECT id,created,grower,field,acres,crop,stage FROM reports ORDER BY id DESC').fetchall()
    st.dataframe([dict(zip(['ID','Date','Grower','Field','Acres','Crop','Stage'],r)) for r in rows],use_container_width=True)
    if rows:
        selected=st.selectbox('Report ID',[r[0] for r in rows]);r=con.execute('SELECT * FROM reports WHERE id=?',(selected,)).fetchone();cols=[x[1] for x in con.execute('PRAGMA table_info(reports)').fetchall()];d=dict(zip(cols,r));d.pop('id',None)
        st.download_button('Download selected PDF',pdf_report(d),file_name=f'crop_report_{selected}.pdf',mime='application/pdf')
else:
    acres=st.number_input('Field acres',min_value=0.0,value=125.0);rate=st.number_input('Product application rate per acre',min_value=0.0,value=1.0);cost=st.number_input('Product cost per unit',min_value=0.0,value=10.0)
    st.metric('Total product needed',f'{acres*rate:,.2f} units');st.metric('Estimated product cost',f'${acres*rate*cost:,.2f}')
    st.caption('Use consistent units. Calculator does not validate label rates or legal application requirements.')
