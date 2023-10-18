
class MenuManager:
    class __MenuManager:
        def open_init_menu(self):
            from pentamusic.menus.init_menu import InitWindow
            InitWindow()

        def open_login_menu(self, is_login):
            from pentamusic.menus.login_menu import LoginWindow
            LoginWindow(is_login)

        def open_main_menu(self):
            from pentamusic.menus.main_menu import MainWindow
            MainWindow()

        def open_sheet_menu(self):
            from pentamusic.menus.sheet_menu import SheetWindow
            SheetWindow()

        def open_usersheet_edit_menu(self, sheet_id):
            from pentamusic.menus.sheet_user_edit_menu import UserSheetEditWindow
            UserSheetEditWindow(sheet_id)

        def open_sheet_edit_menu(self, sheet_id):
            from pentamusic.menus.sheet_edit_menu import SheetEditWindow
            SheetEditWindow(sheet_id)

        def open_sheet_public_menu(self):
            from pentamusic.menus.sheet_public_menu import SheetPublicWindow
            SheetPublicWindow()

        def open_concert_menu(self, show_old):
            from pentamusic.menus.concerts_menu import ConcertWindow
            ConcertWindow(show_old)

        def open_concert_edit_menu(self, user, date):
            from pentamusic.menus.concerts_edit_menu import ConcertEditWindow
            ConcertEditWindow(user, date)

        def open_concert_sheets_menu(self, user, date):
            from pentamusic.menus.concert_sheet_menu import ConcertSheetWindow
            ConcertSheetWindow(user, date)


    # Usamos un singleton
    instance = None

    def __new__(cls):
        if not MenuManager.instance:
            MenuManager.instance = MenuManager.__MenuManager()
        return MenuManager.instance

    def __getattr__(self, item):
        return getattr(self.instance, item)

    def __setattr__(self, key, value):
        return setattr(self.instance, key, value)
