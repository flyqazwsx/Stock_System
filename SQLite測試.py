import sqlite3
from sqlalchemy import create_engine
import tkinter as tk
from tkinter import messagebox
import pandas_datareader as pdr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pylab import mpl
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk
from tkinter import *
from pandastable import Table, TableModel, config
import pandastable
import mysql.connector
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
from mpl_finance import candlestick_ohlc
from matplotlib.dates import DateFormatter
import datetime as dt


conn,cursor=None,None


def btn_open():#開啟
    global conn,cursor
    try:
        
        conn=sqlite3.connect('.\demo.db')
        cursor=conn.cursor()
        label1.config(text=f'以連線資料庫',fg='#80ffff')
    except Exception as e:
        print(e)
    
class Enquiry(Frame):#查詢
    def __init__(self, parent=None):#查詢
        global label1
        try:
            df=pdr.DataReader(entry1.get(),'yahoo','2000')
            datas=df[-1:]
            #list_var.set(datas)
            self.parent = parent
            Frame.__init__(self)
            self.main = self.master
            self.main.geometry('600x500+200+100')
            f1 = Frame(self.main)
            f1.pack(fill=BOTH,expand=1)
            
            
            
            
            
           
            self.table = pt = Table(f1, dataframe=datas,
                                     showtoolbar=True, showstatusbar=True)
            
     
            pt.show()
            #set some options
            options = {'colheadercolor':'green','floatprecision': 5}
            config.apply_options(options, pt)
            pt.show()
            
        
            
            label1.config(text=f'股票代號:{entry1.get()} 以查詢',fg='#80ffff')
            return
        except Exception as e:
                print(e)
    
def btn_close():#關閉
    global conn
    if messagebox.askquestion(title='警告',message='確定離開?')=='yes':
        try:      
            if conn:
                conn.close()
                win.destroy()
        except Exception as e:
                print(e)
def btn_save():#存儲
    global conn,cursor
    try:
        df=pdr.DataReader(entry1.get(),'yahoo','2000')
        #cursor.execute('CREATE TABLE IF NOT EXISTS date (Date,High,Low,Open,Close,Volume,Adj Close                                                , price number)')
        #conn.commit()
        df1=df[-30:]
        x=str(entry1.get())
        a=x.replace('.','_')
        df1.to_sql('date',conn)
        
        
        label1.config(text=f'股票代號:{entry1.get()} 以存入資料庫',fg='#80ffff')
    except Exception as e:
            print(e)
            label1.config(text=f'股票代號:{entry1.get()} 以有資料存在資料庫',fg='red')
            
            
            
def btn_delete():#刪除
    global conn,cursor
    try:
        conn=sqlite3.connect('.\demo.db')
        cursor=conn.cursor()
        df=pdr.DataReader(entry1.get(),'yahoo','2000')
        x=str(entry1.get())
        a=x.replace('.','_')
        if messagebox.askquestion(title='警告',message=f'(確定刪除{x})')=='yes':
        #sql_del=f' DELETE FROM  "2330.tw" ;'
            cursor.execute(" DROP TABLE 'date' ")
            
            conn.commit()
        label1.config(text=f'以刪除{entry1.get()}資料',fg='#80ffff')
    except Exception as e:
            print(e)
            label1.config(text=f'{entry1.get()}無資料存在資料庫',fg='red')
        
            
class view(Frame):#資料檢視
    """Basic test frame for the table"""
    def __init__(self, parent=None):
        global conn,cursor
        try:
            date=pdr.DataReader(entry1.get(),'yahoo','2000')
            x=str(entry1.get())
            
            self.parent = parent
            Frame.__init__(self)
            self.main = self.master
            self.main.geometry('815x700+200+100')
            self.main.title(x)
            f = Frame(self.main)
            f.pack(fill=BOTH,expand=1)
            
            
            
            df =pd.read_sql_query("select * from 'date' ", con=conn)
            
           
            self.table = pt = Table(f, dataframe=df,
                                     showtoolbar=True, showstatusbar=True)
            
     
            pt.show()
            #set some options
            options = {'colheadercolor':'green','floatprecision': 5}
            config.apply_options(options, pt)
            pt.show()
            
        
            return
        except Exception as e:
            print(e)


class plt_KD:#KD圖
    global button8,entry1
    def __init__(self):
        try:
            self.root=tk.Tk()
            self.canvas=tk.Canvas()
            self.root.geometry('1500x900')
            self.figure=self.create_matplotlib()
            self.create_form(self.figure)
            self.root.mainloop()
        except Exception as e:
            print(e)
            
    def ma_avg(data,periods):
        data=pdr.DataReader(entry1.get(),'yahoo','2000')
        data=data[-100:]
        return df['Close'].rolling(periods).mean()
    
   
            
    def create_matplotlib(self):
        global data,ma_avg
        try:
            data=pdr.DataReader(entry1.get(),'yahoo','2000')
            data=data[-100:]
            df_copy=data.copy()
            df_copy['min']= df_copy['Low'].rolling(9).min()
            df_copy['max']= df_copy['High'].rolling(9).max()
            df_copy['RSV']= (df_copy['Close'] - df_copy['min']) /(df_copy['max'] - df_copy['min'])
            #Step2 計算K值
            df_copy = df_copy.dropna()
            K_list = [20]
            for index,rsv in enumerate(list(df_copy['RSV'])):
                K_yestarday= K_list[index]
                K_today =2/3 *K_yestarday + 1/3 *rsv
                K_list.append(K_today)
            df_copy['K'] = K_list[1:]
            #Step3 計算D值
            D_list = [20]
            for index,K in enumerate(list(df_copy['K'])):
                D_yestarday = D_list[index]
                D_today = 2/3 * D_yestarday + 1/3 * K
                D_list.append(D_today)
            df_copy['D'] = D_list[1:]
            use_df= pd.merge(data,df_copy[['K','D']],left_index=True,right_index=True,how='left')
            #
            df=use_df
            data_plot = data.copy()
            data_plot['Datetime'] =data_plot.index
            data_plot = data_plot.reset_index()
            data_plot = data_plot[['Datetime','Open','High','Low','Close']]
            data_plot['Datetime'] = mdates.date2num(data_plot['Datetime'])
            #畫K線圖
            ma_10 = df['Close'].rolling(10).mean()
            ma_20 = df['Close'].rolling(20).mean()
            #ma_50 = df['Close'].rolling(50).mean()
            length = len(data_plot['Datetime'].values[19:])
            f = plt .figure(facecolor='white',figsize=(15,10))
            ax1 = plt.subplot2grid((6,4),(0,0),rowspan=4,colspan=4,facecolor='white')
            
            candlestick_ohlc(ax1,data_plot.values[-length:],width=0.6,colorup='red',colordown='green')
            line1=ax1.plot(data_plot['Datetime'].values[-length:],ma_10[-length:],'#00ccff',label='10 T' ,linewidth=1.5)
            line2=ax1.plot(data_plot['Datetime'].values[-length:],ma_20[-length:],'#6600ff',label='20 T',linewidth=1.5)
            ax1.legend(loc='upper center',ncol=2)
            ax1.grid(True)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            #ax1.axis.label.set_color("black")
            ax1.set_title('日線分析圖 與 KD圖',fontsize=24,pad=20)
            ax1.set_xlabel('日期',fontsize=24,labelpad=12)
            ax1.set_ylabel('指數',fontsize=24,labelpad=12)
            #ax1.legend()
            #ax1.suptitle('Stock Code:2330',color='black',fontsize=16)
            #畫交易量
            ax1v = ax1.twinx()
            ax1v.fill_between(data_plot['Datetime'].values[-length:],0, df.Volume.values[-length:], facecolor='navy', alpha=.4)
            ax1v.axes.yaxis.set_ticklabels([])
            ax1v.grid(False)
            ax1v.set_ylim(0, 3*df.Volume.values.max())
            #加入KD線在下方
            ax2 = plt.subplot2grid((6,4), (4,0), rowspan=1, colspan=4, facecolor='white')
            #ax2 = plt.subplot2grid((6,4), (4,0), sharex=ax1, rowspan=1, colspan=4, facecolor='white')
            ax2.grid(True)
            line3=ax2.plot(data_plot['Datetime'].values[-length:], df.K[-length:],color='#ffcc00',label='D')
            line4=ax2.plot(data_plot['Datetime'].values[-length:], df.D[-length:],color='#00ccff',label='K')
            
            
            ax2.legend()
            return f
        except Exception as e:
            print(e)
            
    def create_form(self,figure):
        global button1,entry1
        try:
            self.canvas=FigureCanvasTkAgg(figure,self.root)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
            
            
            toolbar=NavigationToolbar2Tk(self.canvas,self.root)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        except Exception as e:
            print(e)
    
    
    
class From1: #長條圖
    def __init__(self):
        try:
            self.root=tk.Tk()
            self.canvas=tk.Canvas()
            self.root.geometry('1500x900')
            self.figure=self.create_matplotlib()
            self.create_form(self.figure)
            self.root.mainloop()
        except Exception as e:
            print(e)

    def create_matplotlib(self):
        global button4,entry1,df
        try:
            df=pdr.DataReader(entry1.get(),'yahoo','2000')
            datas=df[-30:]
            f=plt.figure(figsize=(24,12))
            fig1=plt.subplot(3,1,1)
            fig1.grid(True)
           
            x=range(len(datas.index)*2)
            
            line1=fig1.bar(x[0::2],datas['Open'],color='#ff0000',edgecolor='red',label="開盤指數")
            line2=fig1.bar(x[1::2],datas['Close'],color='#33cc33',edgecolor='black',label="收盤指數")
                
            fig1.set_title('30天內的(開盤)與(收盤)指數',fontsize=24,pad=12)
            fig1.set_xlabel('日期',fontsize=24,labelpad=12)
            fig1.set_ylabel('指數',fontsize=24,labelpad=12)
            
            fig1.legend()
            
            fig2=plt.subplot(3,1,3)
            fig2.grid(True)
            
            line3=fig2.bar(x[0::2],datas['High'],color='#ff0000',edgecolor='red',label="最高點指數")
            line4=fig2.bar(x[1::2],datas['Low'],color='#33cc33',edgecolor='black',label="最低點指數")
            fig2.set_title('30天內的(最高點)數與(最低點)指數',fontsize=24,pad=12)
            fig2.set_xlabel('日期',fontsize=24,labelpad=12)
            fig2.set_ylabel('指數',fontsize=24,labelpad=12)
            
            plt.legend()
            return f
        except Exception as e:
            print(e)
    

        
      
    def create_form(self,figure):
        global button1,entry1
        try:
            self.canvas=FigureCanvasTkAgg(figure,self.root)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
            
            
            toolbar=NavigationToolbar2Tk(self.canvas,self.root)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        except Exception as e:
            print(e)


font ={'family' : 'SimHei' , "size" : 24}

matplotlib.rc("font" ,family='MicroSoft YaHei',weight="bold")

class From: #折線圖
    def __init__(self):
        try:
            self.root=tk.Tk()
            self.canvas=tk.Canvas()
            self.root.geometry('1500x900')
            self.figure=self.create_matplotlib()
            self.create_form(self.figure)
            self.root.mainloop()
        except Exception as e:
            print(e)

    def create_matplotlib(self):
        global button1,entry1,df
        try:
            df=pdr.DataReader(entry1.get(),'yahoo','2000')
            datas=df[-30:]
            f=plt.figure(figsize=(24,12))
            fig1=plt.subplot(3,1,1)
            fig1.grid(True)
            line1=fig1.plot(datas.index,datas['Open'],'o-m',label="開盤指數")
            line2=fig1.plot(datas.index,datas['Close'],'^-r',label="收盤指數")
            
            fig1.set_title('30天內的開盤與收盤指數',fontsize=24,pad=12)
            fig1.set_xlabel('日期',fontsize=24,labelpad=12)
            fig1.set_ylabel('指數',fontsize=24,labelpad=12)
            fig1.legend()
            
            fig2=plt.subplot(3,1,3)
            fig2.grid(True)
            line3=fig2.plot(datas.index,datas['High'],'o-m',label="最高點指數")
            ine4=fig2.plot(datas.index,datas['Low'],'^-r',label="最低點指數")
            fig2.set_title('30天內的最高點指數與最低點指數',fontsize=24,pad=12)
            fig2.set_xlabel('日期',fontsize=24,labelpad=12)
            fig2.set_ylabel('指數',fontsize=24,labelpad=12)
            fig2.legend()
            return f
        except Exception as e:
            print(e)
        
      
    def create_form(self,figure):
        global button4,entry1
        try:
            self.canvas=FigureCanvasTkAgg(figure,self.root)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH,expand=1)
            
            
            toolbar=NavigationToolbar2Tk(self.canvas,self.root)
            toolbar.update()
            self.canvas._tkcanvas.pack(side=tk.TOP,fill=tk.BOTH,expand=1)
        except Exception as e:
            print(e)
        

    
    




win=tk.Tk() 
list_var = tk.StringVar()
list_var.set([[]])

win.geometry()
win.title('股票分析系統')

frame1 = tk.Frame(win)
frame1.pack(fill="x")
frame2 = tk.Frame(win)
frame2.pack(fill="x")
frame3 = tk.Frame(win)
frame3.pack(fill="x")
frame4 = tk.Frame(win)
frame4.pack(fill="x")



label1=tk.Label(frame1,text='',font=('Arial',12),bg='black',fg='cyan', anchor="w")
label1.pack(fill='x')

label2=tk.Label(frame1,text='股票查詢系統',font=('Arial',12),width=10,height=2)
label2.pack()

label3= tk.Label(frame2, text="查詢股票代號:", font=('Arial',12))
label3.grid(row=0, column=0)

entry1=tk.Entry(frame2,font=('Arial',12))
entry1.grid(row=0, column=1, columnspan=2)

button0 = tk.Button(frame3, text="開啟", font=('Arial',12), command=btn_open)
button0.grid(row=0, column=0, padx=10, pady=10)

button1 = tk.Button(frame3, text="查詢", font=('Arial',12), command=Enquiry)
button1.grid(row=0, column=1, padx=10, pady=10)

button2 = tk.Button(frame3, text="長條圖", font=('Arial',12), command=From1)
button2.grid(row=0, column=2, padx=10, pady=10)

button3 = tk.Button(frame3, text="  關    閉  ", font=('Arial',12), command=btn_close)
button3.grid(row=0, column=3, padx=10, pady=10)

button4 = tk.Button(frame3, text="存儲", font=('Arial',12), command=btn_save)
button4.grid(row=1, column=0, padx=10, pady=10)

button5 = tk.Button(frame3, text="刪除", font=('Arial',12), command=btn_delete)
button5.grid(row=1, column=1, padx=10, pady=10)

button6 = tk.Button(frame3, text="分析圖", font=('Arial',12), command=From)
button6.grid(row=1, column=2, padx=10, pady=10)

button7 = tk.Button(frame3, text="資料檢視", font=('Arial',12), command=view)
button7.grid(row=1, column=3, padx=10, pady=10)

button8 = tk.Button(frame3, text="KD線", font=('Arial',12), command=plt_KD)
button8.grid(row=2, column=0, padx=10, pady=10)




win.mainloop()
