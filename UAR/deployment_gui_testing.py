import json
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(layout="wide")
git_token = '46874fb7ac5228c0527685ac47af1b95603cca2d'
git_header = {'authorization': 'Bearer  ' + git_token}
releases = requests.get('https://github.cerner.com/api/v3/repos/unified-analytics-reporting/deployment/releases', headers=git_header).json()
release_list = []
tenant_contents = requests.get('https://github.cerner.com/api/v3/repos/unified-analytics-reporting/deployment/contents/configuration/cuar/deployment?ref=23.09', headers=git_header).json()
content_list = []

def get_repo_contents(release):
    url = 'https://github.cerner.com/api/v3/repos/unified-analytics-reporting/deployment/contents/configuration/cuar/repository?ref=' + str(
        release)
    contents = requests.get(url, headers=git_header).json()
    content_def = []
    return_list = []
    for c in contents:
        file = requests.get(c['download_url'], headers=git_header).json()
        content_def.append(file)
    for x in content_def:
        repo_name = x['productName']
        for z in x['repository']:
            version = z['version']
        return_list.append({'name': z['location'].split('/')[1] + '|'  + str(version)})
    return pd.DataFrame(return_list)

def get_recursive_contents(contents_url):
    contents_list = []
    contents = requests.get(contents_url, headers=git_header).json()
    for x in contents['tree']:
        if x['type'] == 'blob' and x['path'] != 'README.md':
            contents_list.append({'object': x['path'], 'link': x['url']})
    return  pd.DataFrame(contents_list)


for x in tenant_contents:
    x['name'] = x['name'].split('-')[0]
    content_list.append({'name' : x['name'], 'download_url': x['download_url']})
for r in releases:
    release_list.append({'release': r['tag_name']})

release_df = pd.DataFrame(release_list)
client_df = pd.DataFrame(content_list)
image_path = Path(__file__).with_name("oracle_9000.jpg").relative_to(Path.cwd())
st.title('Unified Analytics Deployment')
st.sidebar.image(str(image_path),
                 caption="I am completely operational, and all my circuits are functioning perfectly.")
tab1, tab2 = st.tabs(['Query', 'Future'])
with tab1:
    col1, col2 = st.columns(2, gap="small")
    st.header("Query repositories")
    with col1:
        st.subheader("Deployment repo releases ", divider="red")
        s_release = st.selectbox(options=release_df,label='Select release')

    with col2:
        st.subheader("Repository", divider="blue")
        st.write(s_release)
        s_repo = st.selectbox(options=get_repo_contents(s_release), label='Select repository')

    st.subheader("Contents", divider="green")
    contents_url = ("https://github.cerner.com/api/v3/repos/Unified-Analytics-Reporting/" + s_repo.split('|')[0] + "/git/trees/" + s_repo.split('|')[1] + '?recursive=true')
    contents_df = get_recursive_contents(contents_url)
    st.dataframe(contents_df, hide_index=True)