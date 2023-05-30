from __future__ import print_function
import bardapi
import os
import re
import speech_recognition as sr
import flet as ft


from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools


# Replace XXXX with the values you get from __Secure-1PSID
os.environ['_BARD_API_KEY'] = "XXXX"


def generate_quiz(input_text, num_Q):
    bard = bardapi.Bard()
    text = "I create AI application where users can create quiz about what they type, generate me form contains 12 questions (question, four options and the correct Answer),the user type the following: "
    text = text + input_text
    generated_text = bard.get_answer(text)['content']
    for i in range(num_Q//10):
        generated_text += "\n" + \
            bard.get_answer("create 10 more question in the same form")[
                'content']

    lines = generated_text.split("\n")

    list = []
    for i in range(len(lines)-5):
        if len(list) == num_Q:
            break
        if re.search("\d\.(.*)\?", lines[i]):
            if re.search("^(\s*)*(.*)", lines[i+1]) and re.search("^(\s*)\*(.*)", lines[i+2]) and re.search("^(\s*)\*(.*)", lines[i+3]) and re.search("^(\s*)\*(.*)", lines[i+4]) and re.search("^(\s*)\*(.*)", lines[i+5]):
                list.append({
                    "Question": lines[i].split(".")[-1].strip(),
                    "option 1": lines[i+1].split("*")[-1].strip(),
                    "option 2": lines[i+2].split("*")[-1].strip(),
                    "option 3": lines[i+3].split("*")[-1].strip(),
                    "option 4": lines[i+4].split("*")[-1].strip(),
                    "correct anwser": lines[i+5].split(":")[-1].strip()
                })
    return list


def create_form(quiz):
    SCOPES = "https://www.googleapis.com/auth/forms.body"
    DISCOVERY_DOC = "https://forms.googleapis.com/$discovery/rest?version=v1"

    store = file.Storage('assets/token.json')
    creds = None
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(
            'assets/client_secrets.json', SCOPES)
        creds = tools.run_flow(flow, store)

    form_service = discovery.build('forms', 'v1', http=creds.authorize(
        Http()), discoveryServiceUrl=DISCOVERY_DOC, static_discovery=False)
    NEW_FORM = {
        "info": {
            "title": "Quickstart form",
        }
    }
    NEW_QUESTION = {
        "requests": [{
            "createItem": {
                "item": {
                    "title": question["Question"],
                    "questionItem": {
                        "question": {
                            "required": True,
                            "choiceQuestion": {
                                "type": "RADIO",
                                "options": [
                                    {"value": question["option 1"]},
                                    {"value": question["option 2"]},
                                    {"value": question["option 3"]},
                                    {"value": question["option 4"]}
                                ],
                                "shuffle": True
                            }
                        }
                    },
                },
                "location": {
                    "index": 0
                }
            }
        } for question in quiz]
    }
    # Creates the initial form
    result = form_service.forms().create(body=NEW_FORM).execute()

    # Adds the question to the form
    question_setting = form_service.forms().batchUpdate(
        formId=result["formId"], body=NEW_QUESTION).execute()

    # Prints the result to show the question has been added
    get_result = form_service.forms().get(formId=result["formId"]).execute()
    quiz_id = result["formId"]
    quiz_link = f"https://docs.google.com/forms/d/{quiz_id}/viewform"
    return quiz_link


def main(page: ft.Page):
    page.theme_mode = "light"

    def close_banner(e):
        page.banner.open = False
        page.update()
    page.banner = ft.Banner(
        bgcolor=ft.colors.AMBER_100,
        leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED,
                        color=ft.colors.AMBER, size=40),
        content=ft.Text(
            "Oops, there were some errors while trying to delete the file. What would you like me to do?"
        ),
        actions=[
            ft.TextButton("Retry", on_click=close_banner),
            ft.TextButton("Cancel", on_click=close_banner),
        ],
    )

    page.title = "Quiz IA"
    page.scroll = "always"

    def textbox_changed_tb0(e):
        tb0.error_text = None
        tb0.helper_text = None
        if len(str(e.control.value)) > 0 and str(dd.value) != "None":
            b1.disabled = False
        else:
            b1.disabled = True
        page.update()

    def textbox_changed_dd(e):
        if len(str(tb0.value)) > 0:
            b1.disabled = False
        else:
            b1.disabled = True
        page.update()

    def speech_rec(e):
        tb0.error_text = None
        tb0.helper_text = None
        # Initialize recognizer class (for recognizing the speech)
        r = sr.Recognizer()
        # Reading Microphone as source
        # listening the speech and store in audio_text variable
        with sr.Microphone() as source:
            tb0.helper_text = "Talk"
            image1.visible = True
            page.update()
            audio_text = r.listen(source)
            image1.visible = False
            tb0.helper_text = "Time over, thanks"
            page.update()
        # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
        try:
            tb0.value = r.recognize_google(audio_text)
            print("done")
            if len(str(tb0.value)) > 0 and str(dd.value) != "None":
                b1.disabled = False
            else:
                b1.disabled = True
        except:
            tb0.error_text = "sorry, I didn't get that"
        page.update()

    def onclick(e):
        table.rows.append(ft.DataRow(
            [ft.DataCell(
                ft.TextField(
                    expand=True, border_radius=ft.border_radius.all(0),)),
             ft.DataCell(
                ft.TextField(
                    expand=True, border_radius=ft.border_radius.all(0),)),
             ft.DataCell(
                ft.TextField(
                    expand=True, border_radius=ft.border_radius.all(0),)),
             ft.DataCell(
                ft.TextField(
                    expand=True, border_radius=ft.border_radius.all(0),)),
             ft.DataCell(
                ft.TextField(
                    expand=True, border_radius=ft.border_radius.all(0),)),
             ft.DataCell(
                ft.TextField(
                    expand=True, border_radius=ft.border_radius.all(0),))],
            on_select_changed=row_select,
            selected=False
        ))
        page.update()

    def drop(e):
        i = 0
        while i < len(table.rows):
            if table.rows[i].selected:
                table.rows.pop(i)
            else:
                i += 1
        page.update()

    def row_select(e):
        e.control.selected = not e.control.selected
        page.update()
    table = ft.DataTable(
        bgcolor=ft.colors.WHITE,
        border=ft.border.all(2, ft.colors.GREY),
        border_radius=10,
        sort_column_index=0,
        sort_ascending=True,
        heading_row_height=100,
        heading_row_color=ft.colors.WHITE,
        data_row_color={"hovered": ft.colors.TEAL_ACCENT,
                        "focused": ft.colors.WHITE},
        show_checkbox_column=True,
        divider_thickness=0,
        column_spacing=0,
        columns=[
            ft.DataColumn(
                ft.Text("\tQuestion\t", color=ft.colors.TEAL),
            ),
            ft.DataColumn(
                ft.Text("\tOption 1\t", color=ft.colors.TEAL),
            ),
            ft.DataColumn(
                ft.Text("\tOption 2\t", color=ft.colors.TEAL),
            ),
            ft.DataColumn(
                ft.Text("\tOption 3\t", color=ft.colors.TEAL),
            ),
            ft.DataColumn(
                ft.Text("\tOption 4\t", color=ft.colors.TEAL),
            ),
            ft.DataColumn(
                ft.Text("\tCorrect answer\t", color=ft.colors.TEAL),
            ),
        ],
    )
    cv = ft.Column([table], scroll=True)
    rv = ft.Row([cv], scroll=True, expand=1,
                vertical_alignment=ft.CrossAxisAlignment.START)

    def continue_2(e):
        page.banner.open = False
        page.splash = ft.ProgressBar()
        b2.disabled = True
        b3.disabled = True
        b4.disabled = True
        page.update()
        list = []
        for row in table.rows:
            if row.selected:
                list.append({
                    "Question": row.cells[0].content.value,
                    "option 1": row.cells[1].content.value,
                    "option 2": row.cells[2].content.value,
                    "option 3": row.cells[3].content.value,
                    "option 4": row.cells[4].content.value,
                    "correct anwser": row.cells[5].content.value,
                })
        try:
            tb_link.value = create_form(list)
            t2.data = None
            page.go("/form-link")
        except:
            page.banner.open = True
            page.banner.content.value = "Oops, there were some errors while trying to create the form. What would you like me to do?"
            page.banner.actions[0].on_click = continue_2
            page.update()
        page.splash = None
        b2.disabled = False
        b3.disabled = False
        b4.disabled = False
        page.update()

    def continue_1(e):
        page.splash = ft.ProgressBar()
        b1.disabled = True
        b.disabled = True
        page.banner.open = False
        page.update()
        try:
            quiz = generate_quiz(tb0.value, int(dd.value))
            t2.data = quiz
            table.rows = [
                ft.DataRow(
                    cells=[ft.DataCell(
                        ft.TextField(
                            value=i["Question"], expand=True, border_radius=ft.border_radius.all(0),)),
                           ft.DataCell(
                        ft.TextField(
                            value=i["option 1"], expand=True, border_radius=ft.border_radius.all(0),)),
                           ft.DataCell(
                        ft.TextField(
                            value=i["option 2"], expand=True, border_radius=ft.border_radius.all(0),)),
                           ft.DataCell(
                        ft.TextField(
                            value=i["option 3"], expand=True, border_radius=ft.border_radius.all(0),)),
                           ft.DataCell(
                        ft.TextField(
                            value=i["option 4"], expand=True, border_radius=ft.border_radius.all(0),)),
                           ft.DataCell(
                        ft.TextField(
                            value=i["correct anwser"], expand=True, border_radius=ft.border_radius.all(0),))],
                    on_select_changed=row_select,
                    selected=False
                ) for i in quiz]
            s = ""
            for question in quiz:
                s += "\n- "+question["Question"]
                s += "\n\t*"+question["option 1"]
                s += "\n\t*"+question["option 2"]
                s += "\n\t*"+question["option 3"]
                s += "\n\t*"+question["option 4"]
                s += "\n\t\t*"+question["correct anwser"]
            t1.value = s
            page.update()
            page.go("/create-quiz")
        except:
            page.banner.open = True
            page.banner.content.value = "Oops, there were some errors while trying to create the quiz. What would you like me to do?"
            page.banner.actions[0].on_click = continue_1
            page.update()
        b1.disabled = False
        b.disabled = False
        page.splash = None
        page.update()
    def cancel(e):
        page.go("/")
        page.splash = None
        page.banner.open = False
        page.update()
    def copy(e):
        page.set_clipboard(tb_link.value)
        tb_link.helper_text = "copied!"
        page.update()
    t = ft.Text()
    t1 = ft.Text()
    t2 = ft.Text()
    t3 = ft.Text()
    tb1 = ft.TextField(read_only=True, on_focus=copy)
    b = ft.IconButton(tooltip="Start recording ",
                      on_click=speech_rec, icon=ft.icons.MIC)
    tb0 = ft.TextField(label="Entre a pompt here",
                       on_change=textbox_changed_tb0, expand=True, multiline=True,
                       suffix=b,
                       autofocus=True,
                       border_radius=ft.border_radius.all(54),
                       )

    image1 = ft.Image(
        src="assets/GrippingReflectingBasenji-size_restricted.gif", height=100, visible=False)
    b1 = ft.ElevatedButton(
        text="continue ", on_click=continue_1, disabled=True,)
    b2 = ft.ElevatedButton(text="continue ", on_click=continue_2)
    b3 = ft.ElevatedButton("add a row", on_click=onclick)
    b4 = ft.ElevatedButton("drop", on_click=drop)
    b5 = ft.ElevatedButton("Cancel", on_click=cancel)
    dd = ft.Dropdown(
        width=300,
        hint_text="Choose the number of questions",
        options=[
            ft.dropdown.Option(str(i)) for i in range(1, 201)
        ],
        on_change=textbox_changed_dd
    )
    tb_link = ft.TextField(
        read_only=True, on_focus=copy,
        suffix=ft.IconButton(tooltip="Copy link",
                             on_click=copy, icon=ft.icons.COPY),
        expand=True,
        height=100,
        border_radius=ft.border_radius.all(0),
    )
    
    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Row(
                        controls=[
                            ft.Container(content=ft.Image(src="assets/F.gif", height=200,
                                                          fit=ft.ImageFit.FILL),
                                         margin=ft.margin.all(50)
                                         ),
                            ft.Column(
                                expand=True,
                                alignment=ft.alignment.center,
                                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                                controls=[
                                    ft.Text(
                                        spans=[
                                            ft.TextSpan(
                                                "Welcome to Quiz AI\n\tYour Ultimate Quiz Creation Platform!",
                                                ft.TextStyle(
                                                    size=40,
                                                    weight=ft.FontWeight.BOLD,
                                                    foreground=ft.Paint(
                                                        gradient=ft.PaintLinearGradient(
                                                            (0, 300), (700, 200), [
                                                                ft.colors.BLACK, ft.colors.TEAL]
                                                        )
                                                    ),
                                                ),
                                            ),
                                        ],
                                        selectable=True,
                                        height=150,
                                        text_align=ft.TextAlign.CENTER
                                    ),
                                    ft.Text(
                                        "\t\t\tQuiz AI is the innovative solution that revolutionizes the way you create quizzes. Whether you prefer text input or speech recognition, our powerful platform enables you to effortlessly generate engaging quizzes in Google Forms. Get ready to experience a seamless and interactive quiz creation journey like never before.",
                                        overflow=ft.TextOverflow.CLIP,
                                        selectable=True,
                                        size=18.0,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.BLUE_GREY,
                                    ),
                                ]
                            )
                        ]
                    ),
                    ft.Row(
                        controls=[
                            tb0,
                            dd,
                        ],
                        alignment=ft.alignment.top_center,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    image1,
                    b1,
                ],
                bgcolor=ft.colors.WHITE
            )
        )
        if page.route == "/create-quiz":
            page.views.append(
                ft.View(
                    "/create-quiz",
                    [
                        rv,
                        ft.Row(controls=[
                            b2,
                            b3,
                            b4,
                            b5])
                    ],
                    bgcolor=ft.colors.WHITE
                )
            )
        if page.route == "/form-link":
            page.views.append(
                ft.View(
                    "/form-link",
                    [
                        ft.Row(
                            controls=[
                                ft.Container(content=ft.Image(src="assets/F.gif", height=200,
                                                              fit=ft.ImageFit.FILL),
                                             margin=ft.margin.all(50)
                                             ),
                                ft.Column(
                                    expand=True,
                                    alignment=ft.alignment.center,
                                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                                    controls=[
                                        ft.Text(
                                            spans=[
                                                ft.TextSpan(
                                                    "Thank you for choosing Form AI!",
                                                    ft.TextStyle(
                                                        size=40,
                                                        weight=ft.FontWeight.BOLD,
                                                        foreground=ft.Paint(
                                                            gradient=ft.PaintLinearGradient(
                                                                (0, 300), (700, 200), [
                                                                    ft.colors.BLACK, ft.colors.TEAL]
                                                            )
                                                        ),
                                                    ),
                                                ),
                                            ],
                                            selectable=True,
                                            height=100,
                                            text_align=ft.TextAlign.CENTER
                                        ),
                                        ft.Text(
                                            "\t\t\tYour quiz is now ready to be shared. Simply copy the provided link below and share it with your friends, colleagues, or anyone eager to test their knowledge. Let the world discover and engage with your thought-provoking questions..",
                                            selectable=True,
                                            size=18.0,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.colors.BLUE_GREY,
                                        ),
                                    ]
                                )
                            ]
                        ),
                        ft.Row(controls=[
                            ft.ElevatedButton(
                                "Go home", on_click=lambda _: page.go("/"), height=50,
                            ),
                            tb_link
                        ])
                    ],
                    scroll="AUTO",
                    bgcolor=ft.colors.WHITE
                )
            )
        page.update()
    page.on_route_change = route_change
    page.go(page.route)


# , view=ft.WEB_BROWSER
ft.app(target=main, view=ft.WEB_BROWSER, assets_dir="assets")
