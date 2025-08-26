import tkinter as tk
import random
from copy import deepcopy

# 보드에 숫자 넣기 전 유효성 검사
def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

# 스도쿠를 채우는 백트래킹 솔버
def solve(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board, row, col, num):
                        board[row][col] = num
                        if solve(board):
                            return True
                        board[row][col] = 0
                return False
    return True

# 완성된 스도쿠 보드 생성
def generate_full_board():
    board = [[0] * 9 for _ in range(9)]
    solve(board)
    return board

# 숫자를 제거해서 문제 보드 생성
def remove_numbers(board, count):
    board = deepcopy(board)
    removed = 0
    attempts = 0
    while removed < count and attempts < 1000:
        row, col = random.randint(0, 8), random.randint(0, 8)
        if board[row][col] != 0:
            board[row][col] = 0
            removed += 1
        attempts += 1
    return board

# 문자열로 변환 (탭으로 구분)
def board_to_str(board):
    return '\n'.join(['\t'.join(str(cell) if cell != 0 else ' ' for cell in row) for row in board])

# GUI 클래스 정의
class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("sudoku")

        # 상단 입력 및 버튼을 담는 프레임 생성 - 삭제하면 아래로 한줄씩 나열됨
        top_frame = tk.Frame(root)
        top_frame.pack(pady=10)

        # 텍스트 레이블 추가
        tk.Label(top_frame, text="노출 숫자 : ").pack(side="left")

        # 숫자 입력창 추가 (기본값 36, 가운데 정렬)
        self.entry = tk.Entry(top_frame, width=5, justify="center")
        self.entry.insert(0, "36")
        self.entry.pack(side="left", ipady=4) #위아래 여백 추가

        # 생성 버튼 추가
        tk.Button(top_frame, text="생성", width=6, height=2, command=self.generate).pack(side="left", padx=5)

        self.problem_text = tk.Text(root, height=9, width=30)
        self.problem_text.pack()
        self.problem_text.configure(tabs=('25'))  # 탭 간격을 픽셀 단위로 지정(보통 80~100)
        self.problem_text.insert("1.0", "\n\n\n\n문제 생성칸")  # 세로 가운데 정렬을 위한 개행
        self.problem_text.tag_configure("center", justify="center") # 가로 가운데 정렬
        self.problem_text.tag_add("center", "1.0", "end")

        self.answer_text = tk.Text(root, height=9, width=30)
        self.answer_text.pack()
        self.answer_text.configure(tabs=('25'))
        self.answer_text.insert("1.0", "\n\n\n\n답안 생성칸")
        self.answer_text.tag_configure("center", justify="center") # 세로 가운데 정렬
        self.answer_text.tag_add("center", "1.0", "end")

    def generate(self):
        try:
            remain = int(self.entry.get())
            remove_count = 81 - min(81, max(0, remain))
            answer = generate_full_board()
            problem = remove_numbers(answer, remove_count)

            self.problem_text.delete("1.0", tk.END)
            self.problem_text.insert("1.0", board_to_str(problem))
            self.answer_text.delete("1.0", tk.END)
            self.answer_text.insert("1.0", board_to_str(answer))
        except:
            self.problem_text.delete("1.0", tk.END)
            self.problem_text.insert("1.0", "입력 오류")


if __name__ == "__main__":
    import os
    root = tk.Tk()

    # 아이콘 경로 설정: 실행된 py와 같은 폴더의 sudokuico.ico
    app_path = os.path.dirname(__file__)
    icon_path = os.path.join(app_path, "sudokuico.ico")
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)
    app = SudokuApp(root)
    root.mainloop()