import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO
from fetch_books import fetch_book_data

def display_books(book_list):
    result_window = tk.Toplevel()
    result_window.title("도서 검색 결과")
    result_window.geometry("1600x700")

    canvas = tk.Canvas(result_window)
    scrollbar_x = ttk.Scrollbar(result_window, orient="horizontal", command=canvas.xview)
    scrollbar_y = ttk.Scrollbar(result_window, orient="vertical", command=canvas.yview)

    scrollable_frame = ttk.Frame(canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

    container_frame = tk.Frame(scrollable_frame)
    container_frame.pack(fill="both", expand=True)

    for i, book in enumerate(book_list, 1):
        frame = ttk.LabelFrame(container_frame, text=f"\U0001F4D8 도서 {i}번", padding=15)
        frame.pack(side="left", padx=20, pady=20)

        container = tk.Frame(frame)
        container.pack(fill="y")

        try:
            response = requests.get(book["표지 이미지"])
            img = Image.open(BytesIO(response.content)).resize((160, 240))
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(container, image=photo)
            img_label.image = photo
            img_label.pack(side="top", padx=10)
        except:
            img_label = tk.Label(container, text="이미지 없음", width=20, height=10)
            img_label.pack(side="top", padx=10)

        text_frame = tk.Frame(container)
        text_frame.pack(side="top", fill="both", expand=True)

        for k in ["제목", "저자", "출판사", "청구기호", "대출 가능 여부", "권 수"]:
            row = tk.Frame(text_frame)
            row.pack(anchor="w", pady=2)
            tk.Label(row, text=f"{k}:", font=("맑은 고딕", 12, "bold"), anchor="w").pack(side="left")
            tk.Label(row, text=book[k], font=("맑은 고딕", 12), anchor="w", wraplength=300, justify="left").pack(side="left")

        tk.Label(text_frame, text="도서 소개:", font=("맑은 고딕", 12, "bold"), anchor="w").pack(anchor="w", pady=(10, 0))
        intro_box = tk.Text(text_frame, height=6, wrap="word", font=("맑은 고딕", 11), width=45)
        intro = book.get("도서 소개", "도서 소개가 없습니다")  # 기본값 수정
        intro_box.insert("1.0", intro)

        if intro.strip() == "도서 소개가 없습니다":  # 조건 수정
            intro_box.tag_configure("placeholder", foreground="gray", font=("맑은 고딕", 11, "italic"))
            intro_box.tag_add("placeholder", "1.0", "end")

        intro_box.config(state="disabled", relief="flat")
        intro_box.pack(fill="both", padx=5, pady=(0, 10))

    canvas.pack(side="top", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")

    def _on_mousewheel(event):
        canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Shift-MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

def search_books():
    keyword = entry.get().strip()
    if not keyword:
        messagebox.showwarning("입력 오류", "검색할 책 제목을 입력하세요!")
        return

    # 검색 중 표시
    searching_label = tk.Label(root, text="검색 중입니다...", font=("맑은 고딕", 12), fg="blue")
    searching_label.pack(pady=10)
    root.update_idletasks()

    # 입력 및 버튼 비활성화
    entry.config(state="disabled")
    search_button.config(state="disabled")

    try:
        books = fetch_book_data(keyword)
    finally:
        # 검색 완료 후 표시 제거 및 입력/버튼 활성화
        searching_label.destroy()
        entry.config(state="normal")
        search_button.config(state="normal")

    if not books:
        messagebox.showinfo("검색 결과 없음", "검색 결과가 없습니다.")
    else:
        display_books(books)

def on_enter_key(event):
    search_books()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("도서 검색기")
    root.geometry("500x200")

    tk.Label(root, text="검색할 책 제목을 입력하세요:", font=("맑은 고딕", 14)).pack(pady=20)
    entry = tk.Entry(root, font=("맑은 고딕", 14), width=30)
    entry.pack()
    entry.bind("<Return>", on_enter_key)  # 엔터 키 이벤트 바인딩

    search_button = tk.Button(root, text="검색", font=("맑은 고딕", 14), command=search_books)
    search_button.pack(pady=20)

    root.mainloop()