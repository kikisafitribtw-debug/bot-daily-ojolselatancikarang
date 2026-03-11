Import os

Import sqlite3

From datetime import datetime,timedelta

From telegram import Update,ReplyKeyboardMarkup

From telegram.ext import ApplicationBuilder,CommandHandler,MessageHandler,ContextTypes,filters

From apscheduler.schedulers.asyncio import AsyncIOScheduler

Import matplotlib.pyplot as plt



TOKEN=os.getenv(“TOKEN = "8482263728:AAEJI2AozPQZDmUNNmpEYr2_6MOkRDFD_Vw"
ADMIN_ID = 5410925696”)

ADMIN_ID=5410925696



Conn=sqlite3.connect(“ojol.db”,check_same_thread=False)

C=conn.cursor()



c.execute(“””CREATE TABLE IF NOT EXISTS drivers(

id INTEGER PRIMARY KEY,

name TEXT,

phone TEXT,

password TEXT,

mod TEXT

)”””)



c.execute(“””CREATE TABLE IF NOT EXISTS transaksi(

driver TEXT,

tanggal TEXT,

tipe TEXT,

jumlah INTEGER

)”””)



Conn.commit()



Login_user={}



Menu_driver=ReplyKeyboardMarkup([

[“🚕 Order”,”⛽ Bensin”],

[“🍜 Makan”,”🅿 Parkir”],

[“🔧 Servis”,”📊 Saldo”],

[“📅 Rekap Hari”,”📆 Rekap Minggu”],

[“🗓 Rekap Bulan”,”📈 Grafik”],

[“📱 REGIST MOD”,”💬 Chat Admin”],

[“🔑 Reset Password”]

],resize_keyboard=True)



Menu_admin=ReplyKeyboardMarkup([

[“👥 List Driver”],

[“📊 Semua Transaksi”]

],resize_keyboard=True)



Menu_mod=ReplyKeyboardMarkup([

[“Shopee MOD”],

[“Grab MOD”],

[“Gojek MOD”],

[“Maxim MOD”]

],resize_keyboard=True)



Async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):



    If update.message.from_user.id==ADMIN_ID:

        Await update.message.reply_text(“Admin Panel”,reply_markup=menu_admin)

        Return



    Await update.message.reply_text(

“””Daftar:

Daftar nama nomorhp password



Login:

Login nama password

“””)



Async def laporan_harian(app):



    Hari=str(datetime.now().date())



    c.execute(“SELECT driver,tipe,jumlah FROM transaksi WHERE tanggal=?”,(hari,))

    data=c.fetchall()



    laporan=”📊 Laporan Harian\n”



    for d in data:

        laporan+=f”{d[0]} {d[1]} {d[2]}\n”



    await app.bot.send_message(ADMIN_ID,laporan)



async def message(update:Update,context:ContextTypes.DEFAULT_TYPE):



    text=update.message.text

    user=update.message.from_user.id



    if text.startswith(“daftar”):



        data=text.split()



        if len(data)!=4:

            return



        nama=data[1]

        hp=data[2]

        pw=data[3]



        c.execute(“INSERT INTO drivers VALUES(NULL,?,?,?,?)”,(nama,hp,pw,””))

        conn.commit()



        await update.message.reply_text(“Pendaftaran berhasil”)

        return



    if text.startswith(“login”):



        data=text.split()



        nama=data[1]

        pw=data[2]



        c.execute(“SELECT * FROM drivers WHERE name=? AND password=?”,(nama,pw))

        d=c.fetchone()



        if d:

            login_user[user]=nama

            await update.message.reply_text(“Login berhasil”,reply_markup=menu_driver)

        else:

            await update.message.reply_text(“Login gagal”)



        return



    if user not in login_user:

        return



    driver=login_user[user]



    if text==”🚕 Order”:

        context.user_data[“tipe”]=”order”

        await update.message.reply_text(“Masukkan jumlah”)



    elif text==”📱 REGIST MOD”:

        await update.message.reply_text(“Pilih MOD”,reply_markup=menu_mod)



    elif text in [“Shopee MOD”,”Grab MOD”,”Gojek MOD”,”Maxim MOD”]:



        c.execute(“UPDATE drivers SET mod=? WHERE name=?”,(text,driver))

        conn.commit()



        await context.bot.send_message(ADMIN_ID,f”{driver} memakai {text}”)



        await update.message.reply_text(“MOD tersimpan. Silakan chat admin.”)



    elif text==”📈 Grafik”:



        c.execute(“SELECT jumlah FROM transaksi WHERE driver=? AND tipe=’order’”,(driver,))

        data=c.fetchall()



        nilai=[d[0] for d in data]



        plt.plot(nilai)

        plt.title(“Grafik Penghasilan”)



        file=”grafik.png”

        plt.savefig(file)

        plt.close()



        await context.bot.send_photo(user,open(file,”rb”))



    else:



        if text.isdigit():



            tipe=context.user_data.get(“tipe”)



            if tipe:



                jumlah=int(text)

                tanggal=str(datetime.now().date())



                c.execute(

                “INSERT INTO transaksi VALUES(?,?,?,?)”,

                (driver,tanggal,tipe,jumlah)

                )



                Conn.commit()



                Await update.message.reply_text(“Data tersimpan”)



App=ApplicationBuilder().token(TOKEN).build()



App.add_handler(CommandHandler(“start”,start))

App.add_handler(MessageHandler(filters.TEXT,message))



Scheduler=AsyncIOScheduler()



Scheduler.add_job(laporan_harian,”cron”,hour=23,minute=59,args=[app])



Scheduler.start()



App.run_polling()



