const PIECES = {
    WHITE_KING: '♔',
    WHITE_QUEEN: '♕',
    WHITE_ROOK: '♖',
    WHITE_BISHOP: '♗',
    WHITE_KNIGHT: '♘',
    WHITE_PAWN: '♙',
    BLACK_KING: '♚',
    BLACK_QUEEN: '♛',
    BLACK_ROOK: '♜',
    BLACK_BISHOP: '♝',
    BLACK_KNIGHT: '♞',
    BLACK_PAWN: '♟'
};

class ChessGame {
    constructor() {
        this.board = [];
        this.currentPlayer = 'white';
        this.selectedSquare = null;
        this.validMoves = [];
        this.moveHistory = [];
        this.capturedPieces = { white: [], black: [] };
        this.difficulty = 2;
        this.gameOver = false;
        this.initialize();
        this.setupEventListeners();
    }

    initialize() {
        this.board = [
            ['♜', '♞', '♝', '♛', '♚', '♝', '♞', '♜'],
            ['♟', '♟', '♟', '♟', '♟', '♟', '♟', '♟'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['♙', '♙', '♙', '♙', '♙', '♙', '♙', '♙'],
            ['♖', '♘', '♗', '♕', '♔', '♗', '♘', '♖']
        ];
        this.currentPlayer = 'white';
        this.selectedSquare = null;
        this.validMoves = [];
        this.moveHistory = [];
        this.capturedPieces = { white: [], black: [] };
        this.gameOver = false;
        this.renderBoard();
        this.updateStatus();
        this.updateCapturedPieces();
        this.updateMoveHistory();
    }

    setupEventListeners() {
        document.getElementById('newGameBtn').addEventListener('click', () => this.initialize());
        document.getElementById('undoBtn').addEventListener('click', () => this.undoMove());
        document.getElementById('playAgainBtn').addEventListener('click', () => {
            document.getElementById('gameOverModal').classList.remove('active');
            this.initialize();
        });
        document.getElementById('difficulty').addEventListener('change', (e) => {
            this.difficulty = parseInt(e.target.value);
        });
    }

    renderBoard() {
        const boardElement = document.getElementById('chessBoard');
        boardElement.innerHTML = '';

        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                square.className = `square ${(row + col) % 2 === 0 ? 'light' : 'dark'}`;
                square.dataset.row = row;
                square.dataset.col = col;

                const piece = this.board[row][col];
                if (piece) {
                    const pieceElement = document.createElement('span');
                    pieceElement.className = 'piece';
                    pieceElement.textContent = piece;
                    square.appendChild(pieceElement);
                }

                if (this.selectedSquare && this.selectedSquare.row === row && this.selectedSquare.col === col) {
                    square.classList.add('selected');
                }

                if (this.validMoves.some(move => move.row === row && move.col === col)) {
                    square.classList.add('valid-move');
                    if (piece) square.classList.add('has-piece');
                }

                square.addEventListener('click', () => this.handleSquareClick(row, col));
                boardElement.appendChild(square);
            }
        }
    }

    handleSquareClick(row, col) {
        if (this.gameOver || this.currentPlayer === 'black') return;

        const piece = this.board[row][col];

        if (this.selectedSquare) {
            const validMove = this.validMoves.find(move => move.row === row && move.col === col);
            if (validMove) {
                this.makeMove(this.selectedSquare.row, this.selectedSquare.col, row, col);
                this.selectedSquare = null;
                this.validMoves = [];
                this.renderBoard();
                
                if (!this.gameOver) {
                    setTimeout(() => this.botMove(), 500);
                }
            } else if (piece && this.getPieceColor(piece) === this.currentPlayer) {
                this.selectedSquare = { row, col };
                this.validMoves = this.getValidMoves(row, col);
                this.renderBoard();
            } else {
                this.selectedSquare = null;
                this.validMoves = [];
                this.renderBoard();
            }
        } else if (piece && this.getPieceColor(piece) === this.currentPlayer) {
            this.selectedSquare = { row, col };
            this.validMoves = this.getValidMoves(row, col);
            this.renderBoard();
        }
    }

    makeMove(fromRow, fromCol, toRow, toCol) {
        const piece = this.board[fromRow][fromCol];
        const capturedPiece = this.board[toRow][toCol];

        this.moveHistory.push({
            from: { row: fromRow, col: fromCol },
            to: { row: toRow, col: toCol },
            piece: piece,
            captured: capturedPiece,
            player: this.currentPlayer
        });

        if (capturedPiece) {
            const capturedColor = this.getPieceColor(capturedPiece);
            this.capturedPieces[capturedColor].push(capturedPiece);
            this.updateCapturedPieces();
        }

        this.board[toRow][toCol] = piece;
        this.board[fromRow][fromCol] = '';

        const square = document.querySelector(`[data-row="${toRow}"][data-col="${toCol}"]`);
        if (square) square.classList.add('animating');

        if (this.isKingCaptured()) {
            this.endGame();
            return;
        }

        this.currentPlayer = this.currentPlayer === 'white' ? 'black' : 'white';
        this.updateStatus();
        this.updateMoveHistory();
    }

    undoMove() {
        if (this.moveHistory.length === 0 || this.gameOver) return;

        if (this.currentPlayer === 'black' && this.moveHistory.length > 0) {
            const lastMove = this.moveHistory.pop();
            this.board[lastMove.from.row][lastMove.from.col] = lastMove.piece;
            this.board[lastMove.to.row][lastMove.to.col] = lastMove.captured || '';
            
            if (lastMove.captured) {
                const capturedColor = this.getPieceColor(lastMove.captured);
                this.capturedPieces[capturedColor].pop();
            }
        }

        if (this.moveHistory.length > 0) {
            const lastMove = this.moveHistory.pop();
            this.board[lastMove.from.row][lastMove.from.col] = lastMove.piece;
            this.board[lastMove.to.row][lastMove.to.col] = lastMove.captured || '';
            
            if (lastMove.captured) {
                const capturedColor = this.getPieceColor(lastMove.captured);
                this.capturedPieces[capturedColor].pop();
            }
            
            this.currentPlayer = 'white';
        }

        this.selectedSquare = null;
        this.validMoves = [];
        this.renderBoard();
        this.updateStatus();
        this.updateCapturedPieces();
        this.updateMoveHistory();
    }

    botMove() {
        const allMoves = this.getAllPossibleMoves('black');
        if (allMoves.length === 0) {
            this.endGame();
            return;
        }

        let selectedMove;
        
        if (this.difficulty === 1) {
            selectedMove = allMoves[Math.floor(Math.random() * allMoves.length)];
        } else if (this.difficulty === 2) {
            const captureMoves = allMoves.filter(move => this.board[move.to.row][move.to.col] !== '');
            if (captureMoves.length > 0 && Math.random() > 0.3) {
                selectedMove = captureMoves[Math.floor(Math.random() * captureMoves.length)];
            } else {
                selectedMove = allMoves[Math.floor(Math.random() * allMoves.length)];
            }
        } else {
            let bestMove = null;
            let bestScore = -Infinity;
            
            for (const move of allMoves) {
                const score = this.evaluateMove(move);
                if (score > bestScore) {
                    bestScore = score;
                    bestMove = move;
                }
            }
            selectedMove = bestMove;
        }

        if (selectedMove) {
            this.makeMove(selectedMove.from.row, selectedMove.from.col, selectedMove.to.row, selectedMove.to.col);
            this.renderBoard();
        }
    }

    evaluateMove(move) {
        let score = 0;
        const targetPiece = this.board[move.to.row][move.to.col];
        
        if (targetPiece) {
            const pieceValues = {
                '♙': 1, '♟': 1,
                '♘': 3, '♞': 3,
                '♗': 3, '♝': 3,
                '♖': 5, '♜': 5,
                '♕': 9, '♛': 9,
                '♔': 100, '♚': 100
            };
            score += pieceValues[targetPiece] || 0;
        }
        
        score += Math.random() * 2;
        
        return score;
    }

    getAllPossibleMoves(player) {
        const moves = [];
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const piece = this.board[row][col];
                if (piece && this.getPieceColor(piece) === player) {
                    const validMoves = this.getValidMoves(row, col);
                    validMoves.forEach(move => {
                        moves.push({
                            from: { row, col },
                            to: { row: move.row, col: move.col }
                        });
                    });
                }
            }
        }
        return moves;
    }

    getValidMoves(row, col) {
        const piece = this.board[row][col];
        if (!piece) return [];

        const moves = [];
        const color = this.getPieceColor(piece);

        switch (piece) {
            case '♙':
                if (row > 0 && !this.board[row - 1][col]) {
                    moves.push({ row: row - 1, col });
                    if (row === 6 && !this.board[row - 2][col]) {
                        moves.push({ row: row - 2, col });
                    }
                }
                if (row > 0 && col > 0 && this.board[row - 1][col - 1] && this.getPieceColor(this.board[row - 1][col - 1]) !== color) {
                    moves.push({ row: row - 1, col: col - 1 });
                }
                if (row > 0 && col < 7 && this.board[row - 1][col + 1] && this.getPieceColor(this.board[row - 1][col + 1]) !== color) {
                    moves.push({ row: row - 1, col: col + 1 });
                }
                break;

            case '♟':
                if (row < 7 && !this.board[row + 1][col]) {
                    moves.push({ row: row + 1, col });
                    if (row === 1 && !this.board[row + 2][col]) {
                        moves.push({ row: row + 2, col });
                    }
                }
                if (row < 7 && col > 0 && this.board[row + 1][col - 1] && this.getPieceColor(this.board[row + 1][col - 1]) !== color) {
                    moves.push({ row: row + 1, col: col - 1 });
                }
                if (row < 7 && col < 7 && this.board[row + 1][col + 1] && this.getPieceColor(this.board[row + 1][col + 1]) !== color) {
                    moves.push({ row: row + 1, col: col + 1 });
                }
                break;

            case '♖':
            case '♜':
                this.addLinearMoves(moves, row, col, color, [[0, 1], [0, -1], [1, 0], [-1, 0]]);
                break;

            case '♗':
            case '♝':
                this.addLinearMoves(moves, row, col, color, [[1, 1], [1, -1], [-1, 1], [-1, -1]]);
                break;

            case '♕':
            case '♛':
                this.addLinearMoves(moves, row, col, color, [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]]);
                break;

            case '♘':
            case '♞':
                const knightMoves = [[2, 1], [2, -1], [-2, 1], [-2, -1], [1, 2], [1, -2], [-1, 2], [-1, -2]];
                knightMoves.forEach(([dr, dc]) => {
                    const newRow = row + dr;
                    const newCol = col + dc;
                    if (this.isValidPosition(newRow, newCol)) {
                        const targetPiece = this.board[newRow][newCol];
                        if (!targetPiece || this.getPieceColor(targetPiece) !== color) {
                            moves.push({ row: newRow, col: newCol });
                        }
                    }
                });
                break;

            case '♔':
            case '♚':
                const kingMoves = [[0, 1], [0, -1], [1, 0], [-1, 0], [1, 1], [1, -1], [-1, 1], [-1, -1]];
                kingMoves.forEach(([dr, dc]) => {
                    const newRow = row + dr;
                    const newCol = col + dc;
                    if (this.isValidPosition(newRow, newCol)) {
                        const targetPiece = this.board[newRow][newCol];
                        if (!targetPiece || this.getPieceColor(targetPiece) !== color) {
                            moves.push({ row: newRow, col: newCol });
                        }
                    }
                });
                break;
        }

        return moves;
    }

    addLinearMoves(moves, row, col, color, directions) {
        directions.forEach(([dr, dc]) => {
            let newRow = row + dr;
            let newCol = col + dc;
            while (this.isValidPosition(newRow, newCol)) {
                const targetPiece = this.board[newRow][newCol];
                if (!targetPiece) {
                    moves.push({ row: newRow, col: newCol });
                } else {
                    if (this.getPieceColor(targetPiece) !== color) {
                        moves.push({ row: newRow, col: newCol });
                    }
                    break;
                }
                newRow += dr;
                newCol += dc;
            }
        });
    }

    isValidPosition(row, col) {
        return row >= 0 && row < 8 && col >= 0 && col < 8;
    }

    getPieceColor(piece) {
        const whitePieces = ['♔', '♕', '♖', '♗', '♘', '♙'];
        return whitePieces.includes(piece) ? 'white' : 'black';
    }

    isKingCaptured() {
        let whiteKing = false;
        let blackKing = false;

        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const piece = this.board[row][col];
                if (piece === '♔') whiteKing = true;
                if (piece === '♚') blackKing = true;
            }
        }

        return !whiteKing || !blackKing;
    }

    endGame() {
        this.gameOver = true;
        const winner = this.currentPlayer === 'white' ? 'Черные' : 'Белые';
        document.getElementById('gameOverTitle').textContent = '🎉 Игра окончена!';
        document.getElementById('gameOverMessage').textContent = `Победили ${winner}!`;
        document.getElementById('gameOverModal').classList.add('active');
    }

    updateStatus() {
        const statusElement = document.getElementById('statusMessage');
        if (this.gameOver) {
            statusElement.textContent = 'Игра окончена';
        } else {
            statusElement.textContent = this.currentPlayer === 'white' ? 'Ваш ход - белые' : 'Ход бота - черные';
        }
    }

    updateCapturedPieces() {
        document.getElementById('capturedWhite').textContent = this.capturedPieces.white.join(' ');
        document.getElementById('capturedBlack').textContent = this.capturedPieces.black.join(' ');
    }

    updateMoveHistory() {
        const moveListElement = document.getElementById('moveList');
        moveListElement.innerHTML = '';
        
        this.moveHistory.forEach((move, index) => {
            const moveItem = document.createElement('div');
            moveItem.className = `move-item ${move.player}-move`;
            const fromSquare = String.fromCharCode(97 + move.from.col) + (8 - move.from.row);
            const toSquare = String.fromCharCode(97 + move.to.col) + (8 - move.to.row);
            const captureSign = move.captured ? 'x' : '-';
            moveItem.textContent = `${index + 1}. ${move.piece} ${fromSquare}${captureSign}${toSquare}`;
            moveListElement.appendChild(moveItem);
        });
        
        moveListElement.scrollTop = moveListElement.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ChessGame();
});
