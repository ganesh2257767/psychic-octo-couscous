from PySimpleGUI import PopupScrolled, Popup, Radio, Button, Text, In, FileBrowse, InputText, Column, Window, WIN_CLOSED
from pandas import DataFrame, read_excel
from os import getcwd

ico_path = getcwd()
eid_df = DataFrame()

def fmtcols(mylist, cols):
    mylist = [f'{x:^40}' for x in mylist]
    lines = (f'|'.join(mylist[i:i+cols]) for i in range(0, len(mylist), cols))
    return '\n\n'.join(lines)


def from_eid(eid):
    corp_ftax = []
    for i in master_df.index:
        if master_df[3][i] == eid.upper():
            a = str(int(master_df[2][i])) + ' - ' + master_df[4][i].strip()
            corp_ftax.append(a)

    if corp_ftax:
        PopupScrolled(
            f'Following corp/ftax combinations have EID: {eid.upper()}\n\n{fmtcols(corp_ftax, 5)}', size=(100, 20), title=f'{eid.upper()}')

    else:
        Popup(
            f'{eid.upper()} not available or invalid, please check and try again!', title='Error')


def get_corp_ftax(corp, offer_id, df):
    corpftax_altice = set()
    corpftax_legacy = set()
    smb = set()
    
    offer_eid = {df[1][i] for i in df.index if df[2][i] == offer_id}
    for j in master_df.index:
        if master_df[1][j] in corp:
            if master_df[5][j] == 'Y' and master_df[3][j] in offer_eid:
                corpftax_altice.add(
                    str(master_df[2][j])[:-2] + ' - ' + master_df[4][j].strip() + ' - ' + master_df[3][j].strip())

            elif master_df[5][j] == 'N' and master_df[3][j] in offer_eid:
                corpftax_legacy.add(
                     str(master_df[2][j])[:-2] + ' - ' + master_df[4][j].strip() + ' - ' + master_df[3][j].strip())

            else:
                smb.add(str(master_df[2][j])[:-2] + ' - ' + master_df[4][j].strip() + ' - ' + master_df[3][j].strip())


    if corpftax_legacy or corpftax_altice:
        PopupScrolled(
            f"Offer ID {offer_id} available in following corp/ftax combinations \n\nAltice One Combinations\n\n{fmtcols(sorted(corpftax_altice), 3)}\n\nLegacy Combinations\n\n{fmtcols(sorted(corpftax_legacy), 3)}", size=(100, 20), title=f'{offer_id}')
    
    elif smb:
        PopupScrolled(f"<SMB> Offer ID {offer_id} available in following corp/ftax combinations \n\nCombinations for SMB\n\n{fmtcols(sorted(smb), 3)}", size=(100, 20), title=f'{offer_id}')

    else:
        Popup(
            f'Offer {offer_id} not available in {corp} or is invalid!\n\nPlease check offer ID or change corp and try again!', title='Error')


first_layout = [
    [Radio('Search with EID', 'type', key='-SEID-'),
     Radio('Search with Offer ID', 'type', key='-SOID-')],
    [Button('Submit', key='-TYPESUBMIT-')]
]

layout0 = [
    [Text('Upload the Latest Altice West Master Matrix Excel')],
    [In(key='-FILE0-', disabled=True), FileBrowse()],
    [Button('Upload', key='-UPLOAD0-')]
]

layout1 = [
    [Text('Upload the Latest EID Excel')],
    [In(key='-FILE-', disabled=True), FileBrowse()],
    [Button('Upload', key='-UPLOAD-')]
]

layout2 = [
    [Text(key='-SHEETNAME-', size=(50, 1))],
    [Text('Enter Offer ID'), InputText(key='-ID-')],
    [Radio('QA INT', 'corp', key='-QAINT-', default=True),
     Radio('QA 1', 'corp', key='-QA1-'),
     Radio('QA 2', 'corp', key='-QA2-'),
     Radio('QA 3', 'corp', key='-QA3-'),
     Radio('Other corps', 'corp', key='-OTHERS-')],
    [Button('Submit', key='-SUBMIT-'),
     Button('Upload another file', key='-ANOTHER-')]
]

layout3 = [
    [Text('Enter EID'), InputText(key='-EID-')],
    [Button('Submit', key='-SUBMIT1-')]
]

layout = [
    [
        Column(layout0, key='-COL0-'),
        Column(first_layout, key='-FCOL-', visible=False),
        Column(layout1, key='-COL1-', visible=False),
        Column(layout2, key='-COL2-', visible=False),
        Column(layout3, key='-COL3-', visible=False)
    ]
]


window = Window('Corp Ftax Combination checker', layout, resizable=True, icon=ico_path+'\\main1.ico')

upload_flag = True
while True:
    event, values = window.read()
    print(event, values)
    if event in [WIN_CLOSED, 'Cancel']:
        break

    if event == '-UPLOAD0-' and values['-FILE0-']:
        path = values['-FILE0-']
        colnames = [1, 2, 3, 4, 5]

        master_df = read_excel(path, names=colnames)
        window['-COL0-'].update(visible=False)
        window['-FCOL-'].update(visible=True)

    if event == '-TYPESUBMIT-' and values['-SOID-']:
        window['-COL3-'].update(visible=False)
        window['-COL2-'].update(visible=False)
        window['-COL1-'].update(visible=True)

    if event == '-UPLOAD-' and values['-FILE-']:
        upload_flag = False
        path1 = values['-FILE-']
        filename = values['-FILE-'].split('/')[-1]

        eid_df = read_excel(path1, usecols=[0, 1], names=[1, 2])
        window['-SHEETNAME-'].update(f'File Uploaded: {filename}')
        window['-COL1-'].update(visible=False)
        window['-COL2-'].update(visible=True)

    if event == '-SUBMIT-':
        offer_id = values['-ID-']
        if values['-QA2-']:
            corp = [7712, 7709]
        elif values['-QAINT-']:
            corp = [7702, 7704, 7710, 7715]
        elif values['-QA1-']:
            corp = [7708, 7711]
        elif values['-QA3-']:
            corp = [7707, 7714]
        else:
            corp = [7701, 7703, 7705, 7706, 7713]

        try:
            offer_id = int(offer_id)
        except:
            Popup('Enter numerical value')
        else:
            get_corp_ftax(corp, offer_id, eid_df)

    if event == '-ANOTHER-':
        upload_flag = True
        window['-COL1-'].update(visible=True)
        window['-COL2-'].update(visible=False)

    if event == '-TYPESUBMIT-' and values['-SEID-']:
        window['-COL1-'].update(visible=False)
        window['-COL2-'].update(visible=False)
        window['-COL3-'].update(visible=True)

    if event == '-SUBMIT1-':
        eid = values['-EID-']
        from_eid(eid)


window.close()
