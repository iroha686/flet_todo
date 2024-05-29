import flet as ft
from flet import (colors,)

class Task(ft.UserControl):#ft.UserControlクラスを継承した新クラスの作成
    def __init__(self, task_name, task_status_change, task_delete):
        super().__init__()
        self.completed = False#タスクが完了したかどうか
        self.task_name = task_name#タスクの名前
        self.task_status_change = task_status_change#ステータスの変更情報
        self.task_delete = task_delete#タスクの削除情報

    #Todoのチェックボックスと編集、消去するためのコントロールを作成する関数
    def build(self):
        self.display_task = ft.Checkbox(
            #このチェックボックスによりタスクが管理される
            value=False, label=self.task_name, on_change=self.status_changed
        )
        #チェックボックスのタスクの名前を編集するための入力欄
        self.edit_name = ft.TextField(expand=1, on_submit=self.save_clicked)     

        self.display_view = ft.Row(#Row:水平方向に並べるコントロール
            #子コントロールの横方向の位置設定
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            #子コントロールの縦方向の位置設定　.真ん中   
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.display_task,
                ft.Row(
                    spacing=0,#下記の2つのボタンの間隔
                    controls=[
                        #真ん中にアイコンがある丸いボタンであり、このボタンはToDoの編集
                        ft.IconButton(      
                            icon=ft.icons.CREATE_OUTLINED,#アイコンの見た目
                            #ボタンの上にマウスを置いたときに表示されるテキスト
                            tooltip="ToDoを編集",       
                            on_click=self.edit_clicked,
                        ),
                        #ToDoを削除するボタン
                        ft.IconButton(
                            ft.icons.DELETE_OUTLINE,
                            tooltip="ToDoの消去",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = ft.Row(
            visible=False,#このコントロールはデフォルトでは非表示
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.edit_name,
                #ToDoの編集を確定するボタン
                ft.IconButton(
                    icon=ft.icons.DONE_OUTLINE_OUTLINED,
                    icon_color=ft.colors.GREEN,
                    tooltip="ToDoを更新",
                    on_click=self.save_clicked,
                ),
            ],
        )
        
        #Column:コントロールを垂直配列で表示する
        #self.display_viewとself.edit_viewを縦に並べて返す
        return ft.Column(controls=[self.display_view, self.edit_view])


    #非同期関数の定義
    #ToDoを編集するボタンを押したときに実行される関数
    async def edit_clicked(self, e):
        #ToDoを編集するためのTextFieldにToDoの名称を入れる
        self.edit_name.value = self.display_task.label
        #self.display_viewを非表示にする
        self.display_view.visible = False
        #self.edit_viewを表示(デフォルトでは非表示)
        self.edit_view.visible = True
        #TextFieldにフォーカスする
        await self.edit_name.focus_async()
        #self.update_asyncを非同期で呼び出し
        await self.update_async()

    #ToDoの編集を確定するボタンを押したら実行
    async def save_clicked(self, e):
        #TextFieldに入っている文字を新しい名称にする
        self.display_task.label = self.edit_name.value
        self.display_view.visible = True
        self.edit_view.visible = False
        await self.update_async()

    #ToDoの状態を管理するチェックボックスにチェックがされたら実行
    async def status_changed(self, e):
        #タスクの完了状態を変更つまりself.completedがTrueになる
        self.completed = self.display_task.value
        #self.task_status_changeを非同期で呼び出し
        await self.task_status_change(self)

    #ToDoを削除するボタンを押したら実行
    async def delete_clicked(self, e):
        #task_deleteを非同期で呼び出し
        await self.task_delete(self)



class TodoApp(ft.UserControl):
    def build(self):
        self.new_task = ft.TextField(#ToDoを入力する欄の作成
            #on_submit=self.add_clicked : 入力中にEnterをおすとself.add_clickedを実行
            hint_text="何をする？", on_submit=self.add_clicked, expand=True
        )
        #列として表示される要素のまとまり,これにタスクの表示要素が追加されていく
        self.tasks = ft.Column()

        self.filter = ft.Tabs(#タブの作成
            scrollable=False,#タブを水平方向にスクロールできるかどうか
            selected_index=0,#初期状態で選択されているタブ
            on_change=self.tabs_changed,#タブが変更されたときにself.tabs_changed呼び出し
            #タブを３つ作成
            tabs=[ft.Tab(text="すべて"), ft.Tab(text="進行中"), ft.Tab(text="完了")],
        )
        self.items_left = ft.Text("0 個のタスク")

        
        #画面の配置
        return ft.Column(
            width=700,#全体の横幅
            controls=[
                ft.Row(#タイトル
                    [ft.Text(value="Todoリスト", color="pink500", style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        self.new_task,
                        ft.FloatingActionButton(#ToDo追加ボタン
                            icon=ft.icons.ADD, on_click=self.add_clicked, bgcolor="PINK100"
                        ),
                    ],
                ),
                ft.Column(
                    spacing=25,#Column内のコントロールの間隔
                    controls=[
                        self.filter,#タブの追加(呼び出し)
                        self.tasks,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.items_left,
                                ft.OutlinedButton(#完了したタスクを消去するボタン
                                    text="完了したタスクを消去", 
                                    icon="DELETE_OUTLINE",
                                    icon_color="pink200",
                                    on_click=self.clear_clicked, 
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    #新しいToDoが追加されたら呼び出される
    async def add_clicked(self, e):
        if self.new_task.value:#TextFieldが空だと実行されない
            #taskの作成
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            #ToDoが記録されているリストに追加
            self.tasks.controls.append(task)
            #ToDoの入力欄を空にする
            self.new_task.value = ""
            #入力欄にfocusする
            await self.new_task.focus_async()
            #ページの更新
            await self.update_async()

    #タスクの更新をする
    async def task_status_change(self, task):
        await self.update_async()

    #タスクを消去する時に呼び出し
    async def task_delete(self, task):
        self.tasks.controls.remove(task)
        await self.update_async()

    #タブが変更されたときに呼び出し
    async def tabs_changed(self, e):
        await self.update_async()
        

    #完了したタスクを一括消去するときに呼び出し
    async def clear_clicked(self, e):
        #タスクのリストを呼び出してもしタスクが完了していたらそのタスクを削除する
        for task in self.tasks.controls[:]:
            if task.completed:
                await self.task_delete(task)

    #GUIを更新するときに呼び出し
    async def update_async(self):
        #現在選択しているタブの名称をstatusにいれる
        status = self.filter.tabs[self.filter.selected_index].text
        count = 0
        #タスクのリストを呼び出し
        for task in self.tasks.controls:
            #呼び出したtaskの状態をみて表示、非表示を決める
            task.visible = (
                status == "すべて"
                or (status == "進行中" and task.completed == False)
                or (status == "完了" and task.completed)
            )
            if not task.completed:
                count += 1
        
        #進行中のタスクの数を表示
        self.items_left.value = f"進行中のタスクは {count} 個"
        #更新
        await super().update_async()


#GUIの構築
async def main(page: ft.Page):
    page.title = "ToDo アプリ"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    #コントロールを作成してページに追加
    #await page.add_async(...) : 非同期アプリの更新
    await page.add_async(TodoApp())

    

ft.app(main)