import PySimpleGUI as sg
import pandas as pd

eid_df = pd.DataFrame()

def fmtcols(mylist, cols):
    lines = ("\t | \t".join(mylist[i:i+cols]) for i in range(0,len(mylist),cols))
    return '\n\n'.join(lines)


def from_eid(eid):
    corp_ftax = []
    market = set()
    for i in master_df.index:
        if master_df[3][i] == eid.upper():
            a = str(master_df[2][i]) + ' - ' + master_df[4][i].strip()
            corp_ftax.append(a)
            # market.add(master_df[4][i].strip())

    if corp_ftax:
        sg.PopupScrolled(
            f'Following corp/ftax combinations have EID: {eid.upper()}\n', fmtcols(corp_ftax, 5), size=(100, 20), title=f'{eid.upper()}')

    else:
        sg.Popup(
            f'{eid.upper()} not available or invalid, please check and try again!', title='Error')


def get_corp_ftax(corp, id, df):
    corpftax_altice = set()
    corpftax_legacy = set()
    corpftax_altice_unltd = set()
    corpftax_legacy_unltd = set()
    offer_eid = set()
    for i in df.index:
        if df[2][i] == id:
            offer_eid.add(df[1][i])

    for j in master_df.index:
        if master_df[1][j] in corp:
            if master_df[5][j] == 'ALTICE ONE' and master_df[3][j] in offer_eid and master_df[6][j] == 'X':
                corpftax_altice.add(
                    str(master_df[2][j]) + ' - ' + master_df[4][j].strip() + ' - ' + master_df[3][j].strip())

            if master_df[5][j] == 'ALTICE ONE' and master_df[3][j] in offer_eid and master_df[6][j] == 'Unmetered':
                corpftax_altice_unltd.add(
                    str(master_df[2][j]) + ' - ' + master_df[4][j].strip() + ' - ' + master_df[3][j].strip())

            if master_df[5][j] == 'X' and master_df[3][j] in offer_eid and master_df[6][j] == 'X':
                corpftax_legacy.add(
                    str(master_df[2][j]) + ' - ' + master_df[4][j].strip() + ' - ' + master_df[3][j].strip())

            if master_df[5][j] == 'X' and master_df[3][j] in offer_eid and master_df[6][j] == 'Unmetered':
                corpftax_legacy_unltd.add(
                    str(master_df[2][j]) + ' - ' + master_df[4][j].strip() + ' - ' + master_df[3][j].strip())

    if corpftax_legacy or corpftax_altice or corpftax_altice_unltd or corpftax_legacy_unltd:
        sg.PopupScrolled(
            f'Offer ID {id} available in following corp/ftax combinations \n\nAltice One - Unlimited Combinations\n', fmtcols(sorted(corpftax_altice_unltd), 4), '\n\nAltice One - Limited Combinations\n', fmtcols(sorted(corpftax_altice), 4), '\n\nLegacy - Unlimited Combinations\n', fmtcols(sorted(corpftax_legacy_unltd), 4), '\n\nLegacy - Limited Combinations\n', fmtcols(sorted(corpftax_legacy), 4), size=(100, 20), title=f'{id}')
    else:
        sg.Popup(
            f'Offer {id} not available in {corp} or is invalid!\n\nPlease check offer ID or change corp and try again!', title='Error')


first_layout = [
    [sg.Radio('Search with EID', 'type', key='-SEID-'),
     sg.Radio('Search with Offer ID', 'type', key='-SOID-')],
    [sg.Button('Submit', key='-TYPESUBMIT-')]
]

layout0 = [
    [sg.Text('Upload the Latest Altice West Master Matrix Excel')],
    [sg.In(key='-FILE0-', disabled=True), sg.FileBrowse()],
    [sg.Button('Upload', key='-UPLOAD0-')]
]

layout1 = [
    [sg.Text('Upload the Latest EID Excel')],
    [sg.In(key='-FILE-', disabled=True), sg.FileBrowse()],
    [sg.Button('Upload', key='-UPLOAD-')]
]

layout2 = [
    [sg.Text(key='-SHEETNAME-', size=(50, 1))],
    [sg.Text('Enter Offer ID'), sg.InputText(key='-ID-')],
    [sg.Radio('QA 2', 'corp', key='-QA2-', default=True), sg.Radio('QA INT',
                                                                   'corp', key='-QAINT-'), sg.Radio('Other corps', 'corp', key='-OTHERS-')],
    [sg.Button('Submit', key='-SUBMIT-'),
     sg.Button('Upload another file', key='-ANOTHER-')]
]

layout3 = [
    [sg.Text('Enter EID'), sg.InputText(key='-EID-')],
    [sg.Button('Submit', key='-SUBMIT1-')]
]

layout = [
    [
        sg.Column(layout0, key='-COL0-'),
        sg.Column(first_layout, key='-FCOL-', visible=False),
        sg.Column(layout1, key='-COL1-', visible=False),
        sg.Column(layout2, key='-COL2-', visible=False),
        sg.Column(layout3, key='-COL3-', visible=False)]
]


window = sg.Window('Corp Ftax Combination checker', layout, resizable=True, icon=r'main.ico')

upload_flag = True
while True:
    event, values = window.read()
    print(f'Event: {event} | Values: {values}')
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    if event == '-UPLOAD0-':
        if values['-FILE0-']:
            path = values['-FILE0-']
            columns = [0, 2, 3, 7, 12, 13]
            colnames = [1, 2, 3, 4, 5, 6]

            master_df = pd.read_excel(path, usecols=columns, names=colnames)
            window['-COL0-'].update(visible=False)
            window['-FCOL-'].update(visible=True)

    if event == '-TYPESUBMIT-' and values['-SOID-']:
        window['-COL3-'].update(visible=False)
        window['-COL2-'].update(visible=False)
        window['-COL1-'].update(visible=True)

    if event == '-UPLOAD-':
        if values['-FILE-']:
            upload_flag = False
            path1 = values['-FILE-']
            filename = values['-FILE-'].split('/')[-1]

            eid_df = pd.read_excel(path1, usecols=[0, 1], names=[1, 2])
            window['-SHEETNAME-'].update(f'File Uploaded: {filename}')
            window['-COL1-'].update(visible=False)
            window['-COL2-'].update(visible=True)

    if event == '-SUBMIT-':
        offer_id = values['-ID-']
        if values['-QA2-']:
            corp = [7712, 7709]
        elif values['-QAINT-']:
            corp = [7702, 7704, 7710, 7715]
        else:
            corp = [7701, 7703, 7705, 7706, 7707, 7708, 7711, 7713, 7714]

        try:
            offer_id = int(offer_id)
        except:
            sg.Popup('Enter numerical value')
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
