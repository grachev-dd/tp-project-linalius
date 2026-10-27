import telegram
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

custom_request = HTTPXRequest(
    connect_timeout=30.0,
    read_timeout=30.0,
    connection_pool_size=16
)



CHOOSE, DETRECEIVE, MULTRECEIVE1, MULTRECEIVE2, ENDING, INVRECEIVE, SOLVECHOOSE, SOLVEAXB1, SOLVEAXB2, SOLVEXAB1, SOLVEXAB2  = range(11)

def determinant(matrix: list) -> float: # метод гаусса
    n = len(matrix)
    a = [row[:] for row in matrix]
    det = 1.0

    for i in range(n):
        pivot = i
        for r in range(i, n):
            if abs(a[r][i]) > 1e-12:
                pivot = r
                break
        else:
            return 0.0
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            det *= -1

        det *= a[i][i]

        for r in range(i + 1, n):
            factor = a[r][i] / a[i][i]
            for c in range(i, n):
                a[r][c] -= factor * a[i][c]
    return det

def mult(m1: list, m2: list) -> list:
    size = len(m2)
    size1 = len(m2[0])
    size2 = len(m1)

    m = [[0] * size2 for _ in range(size1)]
    for i in range(size2):
        for j in range(size1):
            summ = 0
            for k in range(size):
                summ += (m1[i][k] * m2[k][j])
            m[i][j] = summ

    return m

def invert(m: list) -> list:
    size = len(m)
    det = determinant(m)
    inv = [[0] * size for _ in range(size)]
    m1 = [[0] * size for _ in range(size)]
    for row in range(size):
        for col in range(size):
            m1[row][col] = m[col][row]
    for row in range(size):
        for col in range(size):
            minor = [x[:col] + x[col + 1:] for x in (m1[:row] + m1[row + 1:])]
            alg = ((-1) ** (row + col)) * determinant(minor) / det
            inv[row][col] = alg
    return inv

async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я Линалиус - твой помощник по матрицам. Буду рад тебе помочь с линейной алгеброй!")
    await update.message.reply_text("Выбери что ты хочешь сделать:\n\n1) Посчитать определитель матрицы\n2) Умножить матрицу NxM на матрицу MxL\n3) Посчитать обратную матрицу\n4) Решить матричное линейное уравнение")

    return CHOOSE


async def choose(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        choice = int(update.message.text)
        if choice == 1:
            await update.message.reply_text("Введи квадратную матрицу, а я посчитаю определитель")
            return DETRECEIVE
        elif choice == 2:
            await update.message.reply_text("Введи первую матрицу для умножения")
            return MULTRECEIVE1
        elif choice == 3:
            await update.message.reply_text("Введи квадратную матрицу, а я верну обратную ей")
            return INVRECEIVE
        elif choice == 4:
            await update.message.reply_text("Выберите тип уравнения:\n\n1) A * X = B\n2) X * A = B")
            return SOLVECHOOSE
        else:
            await update.message.reply_text("Такого варианта нет, выбери из функций 1, 2, 3 или 4")
            return CHOOSE
    except ValueError:
        await update.message.reply_text("Тебе нужно ввести номер функции 1, 2, 3 или 4")
        return CHOOSE


async def solve_choose(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        choice = int(update.message.text)
        if choice == 1:
            await update.message.reply_text("Введите квадратную матрицу A")
            return SOLVEAXB1
        elif choice == 2:
            await update.message.reply_text("Введите квадратную матрицу A")
            return SOLVEXAB1
        else:
            await update.message.reply_text("Такого варианта нет, выбери из типов 1 или 2")
            return SOLVECHOOSE
    except ValueError:
        await update.message.reply_text("Тебе нужно ввести тип уравнения 1 или 2")
        return SOLVECHOOSE



async def solve_axb1(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = list(update.message.text.split("\n"))
        for i in range(len(m)):
            m[i] = list(map(float, m[i].split()))
        if len(m) != len(m[0]):
            await update.message.reply_text("Введенная матрица А не квадратная. Решить такое уравнение нельзя. Введите другую матрицу или отмените операцию с помощью /cancel")
            return SOLVEAXB1
        if abs(determinant(m)) < 1e-12:
            await update.message.reply_text("Определитель матрицы А равен 0. Решить такое уравнение нельзя. Введите другую матрицу или отмените операцию с помощью /cancel")
            return SOLVEAXB1
        context.user_data['solveMatrix1'] = m
        await update.message.reply_text("Введите матрицу B")
        return SOLVEAXB2
    except ValueError:
        await update.message.reply_text("Вы ввели не матрицу. Попробуйте еще раз или отмените операцию с помощью /cancel")
        return SOLVEAXB1




async def solve_xab1(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = list(update.message.text.split("\n"))
        for i in range(len(m)):
            m[i] = list(map(float, m[i].split()))
        if len(m) != len(m[0]):
            await update.message.reply_text("Введенная матрица А не квадратная. Решить такое уравнение нельзя. Введите другую матрицу или отмените операцию с помощью /cancel")
            return SOLVEXAB1
        if abs(determinant(m)) < 1e-12:
            await update.message.reply_text("Определитель матрицы А равен 0. Решить такое уравнение нельзя. Введите другую матрицу или отмените операцию с помощью /cancel")
            return SOLVEXAB1
        context.user_data['solveMatrix1'] = m
        await update.message.reply_text("Введите матрицу B")
        return SOLVEXAB2
    except ValueError:
        await update.message.reply_text("Вы ввели не матрицу. Попробуйте еще раз или отмените операцию с помощью /cancel")
        return SOLVEXAB1



async def solve_axb2(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m2 = list(update.message.text.split("\n"))
        for i in range(len(m2)):
            m2[i] = list(map(float, m2[i].split()))
        m1 = context.user_data.get('solveMatrix1')

        if len(m2) != len(m1):
            await update.message.reply_text("Матрица B не может получиться такого размера. Введите возможную или отмените операцию с помощью /cancel")
            return SOLVEAXB2

        else:
            size = len(m2)
            size1 = len(m2[0])
            ans = mult(invert(m1), m2)
            final = f'Получилась матрица X размера {size}x{size1}:\n'

            for i in range(size):
                final += '\n'
                for j in range(size1):
                    if j: final += ' '
                    if abs(ans[i][j] - int(ans[i][j])) < 1e-5:
                        final += f'{int(ans[i][j])}'
                    else:
                        final += f'{ans[i][j]:.4f}'
            final += '\n\nЧтобы продолжить отправьте любое сообщение'
            await update.message.reply_text(final)
            return ENDING

    except ValueError:
        await update.message.reply_text("Вы ввели не матрицу. Попробуйте еще раз или отмените операцию с помощью /cancel")
        return SOLVEAXB2



async def solve_xab2(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m2 = list(update.message.text.split("\n"))
        for i in range(len(m2)):
            m2[i] = list(map(float, m2[i].split()))
        m1 = context.user_data.get('solveMatrix1')

        if len(m2) != len(m1[0]):
            await update.message.reply_text("Матрица B не может получиться такого размера. Введите возможную или отмените операцию с помощью /cancel")
            return SOLVEXAB2

        else:
            size = len(m2)
            size1 = len(m2[0])
            ans = mult(m2, invert(m1))

            final = f'Получилась матрица X размера {size}x{size1}:\n'

            for i in range(size):
                final += '\n'
                for j in range(size1):
                    if j: final += ' '
                    if abs(ans[i][j] - int(ans[i][j])) < 1e-5:
                        final += f'{int(ans[i][j])}'
                    else:
                        final += f'{ans[i][j]:.4f}'
            final += '\n\nЧтобы продолжить отправьте любое сообщение'
            await update.message.reply_text(final)
            return ENDING

    except ValueError:
        await update.message.reply_text("Вы ввели не матрицу. Попробуйте еще раз или отмените операцию с помощью /cancel")
        return SOLVEXAB2



async def det_receive(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = list(update.message.text.split("\n"))
        for i in range(len(m)):
            m[i] = list(map(float, m[i].split()))

        if len(m) != len(m[0]):
            await update.message.reply_text("Матрица должна быть квадратной. Введите другую или отмените операцию с помощью /cancel")
            return DETRECEIVE

        else:
            det = determinant(m)
            if abs(det - int(det)) < 1e-5:
                await update.message.reply_text(f'Определитель вашей матрицы равен:\n\n{int(det)}\n\nЧтобы продолжить отправьте любое сообщение')
            else:
                await update.message.reply_text(f'Определитель вашей матрицы равен:\n\n{det:.4f}\n\nЧтобы продолжить отправьте любое сообщение')
            return ENDING

    except ValueError:
        await update.message.reply_text("Вы ввели не матрицу. Попробуйте еще раз или отмените операцию с помощью /cancel")
        return DETRECEIVE



async def mult_receive1(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = list(update.message.text.split("\n"))
        for i in range(len(m)):
            m[i] = list(map(float, m[i].split()))

        context.user_data['multMatrix1'] = m
        await update.message.reply_text("Введи вторую матрицу для умножения")

        return MULTRECEIVE2
    except ValueError:
        await update.message.reply_text("Вы ввели не матрицу. Попробуйте еще раз или отмените операцию с помощью /cancel")
        return MULTRECEIVE1


async def mult_receive2(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m2 = list(update.message.text.split("\n"))
        for i in range(len(m2)):
            m2[i] = list(map(float, m2[i].split()))
        m1 = context.user_data.get('multMatrix1')

        if len(m2) != len(m1[0]):
            await update.message.reply_text("Такие матрицы нельзя перемножить. Введите возможную или отмените операцию с помощью /cancel")
            return MULTRECEIVE2

        else:
            size = len(m2)
            size1 = len(m2[0])
            size2 = len(m1)
            mul = mult(m1, m2)
            final = f'Получилась матрица размера {size2}x{size1}:\n'

            for i in range(size):
                final += '\n'
                for j in range(size):
                    if j: final += ' '
                    if abs(mul[i][j] - int(mul[i][j])) < 1e-5:
                        final += f'{int(mul[i][j])}'
                    else:
                        final += f'{mul[i][j]:.4f}'
            final += '\n\nЧтобы продолжить отправьте любое сообщение'
            await update.message.reply_text(final)
            return ENDING

    except ValueError:
        await update.message.reply_text("Вы ввели не матрицу. Попробуйте еще раз или отмените операцию с помощью /cancel")
        return MULTRECEIVE2

async def inv_receive(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        m = list(update.message.text.split("\n"))
        for i in range(len(m)):
            m[i] = list(map(float, m[i].split()))

        if len(m) != len(m[0]):
            await update.message.reply_text("Матрица должна быть квадратной. Введите другую или отмените операцию с помощью /cancel")
            return INVRECEIVE

        det = determinant(m)
        if abs(det) < 1e-12:
            await update.message.reply_text("Определитель этой матрицы равен 0. Обратную к ней построить невозможно. Введите другую или отмените операцию с помощью /cancel")
            return INVRECEIVE

        else:
            size = len(m)
            inv = [[0] * size for _ in range(size)]
            m1 = [[0] * size for _ in range(size)]
            for row in range(size):
                for col in range(size):
                    m1[row][col] = m[col][row]
            for row in range(size):
                for col in range(size):
                    minor = [x[:col] + x[col + 1:] for x in (m1[:row] + m1[row + 1:])]
                    alg = ((-1) ** (row + col)) * determinant(minor) / det
                    inv[row][col] = alg
            final = f'Получилась следующая обратная матрица:\n'

            for i in range(size):
                final += '\n'
                for j in range(size):
                    if j: final += ' '
                    if abs(inv[i][j] - int(inv[i][j])) < 1e-5:
                        final += f'{int(inv[i][j])}'
                    else:
                        final += f'{inv[i][j]:.4f}'
            final += '\n\nЧтобы продолжить отправьте любое сообщение'
            await update.message.reply_text(final)
            return ENDING


    except ValueError:
        await update.message.reply_text("Вы ввели не матрицу. Попробуйте еще раз или отмените операцию с помощью /cancel")
        return INVRECEIVE


async def ending(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    textTmp = update.message.text
    if textTmp:
        await update.message.reply_text("Возвращаемся к выбору...")
        await update.message.reply_text("Выбери что ты хочешь сделать:\n\n1) Посчитать определитель матрицы\n2) Умножить матрицу NxM на матрицу MxL\n3) Посчитать обратную матрицу\n4) Решить матричное линейное уравнение")
    return CHOOSE

async def cancel(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена. Чтобы продолжить введите /start")
    return ConversationHandler.END



conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose)],
        DETRECEIVE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, det_receive)],
        MULTRECEIVE1:   [MessageHandler(filters.TEXT & ~filters.COMMAND, mult_receive1)],
        MULTRECEIVE2:   [MessageHandler(filters.TEXT & ~filters.COMMAND, mult_receive2)],
        INVRECEIVE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, inv_receive)],
        SOLVECHOOSE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, solve_choose)],
        SOLVEAXB1:    [MessageHandler(filters.TEXT & ~filters.COMMAND, solve_axb1)],
        SOLVEAXB2:    [MessageHandler(filters.TEXT & ~filters.COMMAND, solve_axb2)],
        SOLVEXAB1:    [MessageHandler(filters.TEXT & ~filters.COMMAND, solve_xab1)],
        SOLVEXAB2:    [MessageHandler(filters.TEXT & ~filters.COMMAND, solve_xab2)],
        ENDING: [MessageHandler(filters.TEXT & ~filters.COMMAND, ending)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

if __name__ == "__main__":
    TOKEN = "TOKEN"
    app = ApplicationBuilder().token(TOKEN).request(custom_request).get_updates_request(custom_request).build()

    app.add_handler(conv_handler)

    print("Бот запущен...")
    app.run_polling()
