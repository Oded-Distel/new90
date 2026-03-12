from __future__ import annotations

import tkinter as tk
from tkinter import messagebox


class TicTacToeApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tic-Tac-Toe (X/O)")
        self.root.resizable(False, False)

        self.current_player = "X"
        self.board: list[list[str | None]] = [[None] * 3 for _ in range(3)]

        self.status_var = tk.StringVar(value="Turn: X")

        container = tk.Frame(root, padx=14, pady=14)
        container.grid(row=0, column=0)

        header = tk.Frame(container)
        header.grid(row=0, column=0, sticky="ew")

        title = tk.Label(header, text="Tic-Tac-Toe", font=("Helvetica", 18, "bold"))
        title.grid(row=0, column=0, sticky="w")

        status = tk.Label(header, textvariable=self.status_var, font=("Helvetica", 11))
        status.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.grid_frame = tk.Frame(container, pady=12)
        self.grid_frame.grid(row=1, column=0)

        self.buttons: list[list[tk.Button]] = []
        for r in range(3):
            row: list[tk.Button] = []
            for c in range(3):
                btn = tk.Button(
                    self.grid_frame,
                    text="",
                    width=6,
                    height=3,
                    font=("Helvetica", 22, "bold"),
                    command=lambda rr=r, cc=c: self.play(rr, cc),
                )
                btn.grid(row=r, column=c, padx=6, pady=6)
                row.append(btn)
            self.buttons.append(row)

        footer = tk.Frame(container)
        footer.grid(row=2, column=0, sticky="ew")

        restart = tk.Button(footer, text="Restart", command=self.reset, width=12)
        restart.grid(row=0, column=0, sticky="w")

        quit_btn = tk.Button(footer, text="Quit", command=self.root.destroy, width=12)
        quit_btn.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self._game_over = False

    def play(self, r: int, c: int) -> None:
        if self._game_over:
            return
        if self.board[r][c] is not None:
            return

        self.board[r][c] = self.current_player
        self.buttons[r][c].config(text=self.current_player, state="disabled")

        winner = self.check_winner()
        if winner:
            self._game_over = True
            self.status_var.set(f"Winner: {winner}")
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self._disable_all()
            return

        if self.is_draw():
            self._game_over = True
            self.status_var.set("Draw")
            messagebox.showinfo("Game Over", "It's a draw!")
            self._disable_all()
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self.status_var.set(f"Turn: {self.current_player}")

    def _disable_all(self) -> None:
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(state="disabled")

    def reset(self) -> None:
        self.current_player = "X"
        self.board = [[None] * 3 for _ in range(3)]
        self._game_over = False
        self.status_var.set("Turn: X")
        for r in range(3):
            for c in range(3):
                self.buttons[r][c].config(text="", state="normal")

    def check_winner(self) -> str | None:
        b = self.board
        lines: list[list[tuple[int, int]]] = []

        for r in range(3):
            lines.append([(r, 0), (r, 1), (r, 2)])
        for c in range(3):
            lines.append([(0, c), (1, c), (2, c)])

        lines.append([(0, 0), (1, 1), (2, 2)])
        lines.append([(0, 2), (1, 1), (2, 0)])

        for line in lines:
            values = [b[r][c] for r, c in line]
            if values[0] is not None and values.count(values[0]) == 3:
                return values[0]
        return None

    def is_draw(self) -> bool:
        return all(self.board[r][c] is not None for r in range(3) for c in range(3))


def main() -> None:
    root = tk.Tk()
    app = TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
