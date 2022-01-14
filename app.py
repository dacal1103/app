import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import pymysql


def actualizar():
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='nora.566', db='referencias', port=3306, charset='utf8')
    cl = db.cursor()
    dato_historico = "select * from referencias"
    cl.execute(dato_historico)
    info = cl.fetchall()
    db.commit()
    cl.close()
    db.close()
    ID = pd.DataFrame(info).tail(1)[0]
    ID = int(ID)+1
    return ID

def lectura_ingreso():
    lectura =  pymysql.connect(host='127.0.0.1', user='root', passwd='nora.566', db='referencias', port=3306, charset='utf8')
    lc = lectura.cursor()
    hist = "select * from referencias"
    lc.execute(hist)
    datos_ingreso = lc.fetchall()
    lectura.close()
    lc.close()
    datos_ingresos =  pd.DataFrame(datos_ingreso)
    return datos_ingresos

def acutualizar_salida():
    db2 = pymysql.connect(host='127.0.0.1', user='root', passwd='nora.566', db='referencias', port=3306, charset='utf8')
    cl2 = db2.cursor()
    dato_salida = "select * from salidas"
    cl2.execute(dato_salida)
    salidas = cl2.fetchall()
    db2.commit()
    cl2.close()
    db2.close()
    ID2 = pd.DataFrame(salidas).tail(1)[0]
    ID2 = int(ID2)+1
    return ID2

def lectura_salida():
    db2 = pymysql.connect(host='127.0.0.1', user='root', passwd='nora.566', db='referencias', port=3306, charset='utf8')
    cl2 = db2.cursor()
    dato_salida = "select * from salidas"
    cl2.execute(dato_salida)
    salidas = cl2.fetchall()
    db2.commit()
    cl2.close()
    db2.close()
    datos_salida =  pd.DataFrame(salidas)
    return datos_salida

def procesamiento(datos_entrada,datos_salida):
    #datos_ingreso = datos_entrada.drop([0])
    datos_entrada.columns = ['ID','referencia','valor_total','valor_unitario','talla','color','cantidad']
    datos_ingreso = datos_entrada.pivot_table(index = ['referencia','color','talla'], aggfunc=np.sum)
    datos_ingreso = datos_ingreso.reset_index()
    #datos_salida = datos_salida.drop([0])
    datos_salida.columns = ['ID','talla','referencia','color','cantidad','valor_unitario','valor_total']
    datos_salida['cantidad'] = datos_salida['cantidad']*-1
    datos_salida = datos_salida.pivot_table(index = ['referencia','color','talla'], aggfunc=np.sum)
    datos_salida = datos_salida.reset_index()
    #datos_ingreso = datos_ingreso.drop(columns=['ID'])
    #datos_salida = datos_salida.drop(columns=['ID'])
    datos_finales = pd.concat([datos_ingreso,datos_salida])
    datos_finales = datos_finales.pivot_table(index = ['referencia','color','talla'], aggfunc=np.sum)
    datos_finales = datos_finales.reset_index()
    return datos_finales

def cargar_tt():
    db3 = pymysql.connect(host='127.0.0.1', user='root', passwd='nora.566', db='referencias', port=3306, charset='utf8')
    cl2 = db3.cursor()
    datos_salida = "select * from saldos"
    cl2.execute(datos_salida)
    finales = cl2.fetchall()
    db3.commit()
    cl2.close()
    db3.close()
    finales = pd.DataFrame(finales).tail(1)[0]
    ID3 = int(finales)+1
    return ID3



conexion = mysql.connector.connect(user='root',password='nora.566',host='127.0.0.1',database='referencias',port='3306')
cursor = conexion.cursor()

class Aplicativo:
    def referencias(self,ruta):
        self.data =  pd.read_excel(ruta, sheet_name='referencias')

    def cargar_datos(self,talla,referencia,color,cantidad,valor_u):
        cargar =  [talla,referencia,color,cantidad,valor_u]
        valor_t = int(cargar[3])*int(cargar[4])
        cargar.append(valor_t)
        return cargar

    def cargar_datos_salida(self,talla,referencia,color,cantidad,valor_u):
        cargar_salida =  [talla,referencia,color,cantidad,valor_u]
        valor_t_salida = int(cargar_salida[3])*int(cargar_salida[4])
        cargar_salida.append(valor_t_salida)
        return cargar_salida

    def cargar(self,datos_sql,ID):
        query = f"INSERT INTO referencias (ID,talla,referencia,color,cantidad,valor_unitario,valor_total) VALUES ('{ID}','{datos_sql[0]}','{datos_sql[1]}','{datos_sql[2]}','{datos_sql[3]}','{datos_sql[4]}','{datos_sql[5]}')"
        cursor.execute(query)
        conexion.commit()

    def cargar_salida(self,datos,ID_salida):
        query_2 = f"INSERT INTO salidas (ID,talla,referencia,color,cantidad,valor_unitario,valor_total) VALUES ('{ID_salida}','{datos[0]}','{datos[1]}','{datos[2]}','{datos[3]}','{datos[4]}','{datos[5]}')"
        cursor.execute(query_2)
        conexion.commit()

    def cargar_finales(self,datos):

        query_3 = f"INSERT INTO saldos(ID,referencia,color,talla,cantidad,valor_total,valor_unitario)VALUES('{datos[0]}','{datos[1]}','{datos[2]}','{datos[3]}','{datos[4]}','{datos[5]}','{datos[6]}')"
        cursor.execute(query_3)
        conexion.commit()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def inve():
    if request.method == 'POST':
        talla = request.form.get('talla')
        referencia = request.form.get('referencia')
        color = request.form.get('color')
        cantidad = request.form.get('cantidad')
        valor_u =  request.form.get('valoru')

        ID = actualizar()
        c = Aplicativo()
        sql = c.cargar_datos(talla,referencia,color,cantidad,valor_u)
        c.cargar(sql,ID)

        valor_t = int(cantidad)*int(valor_u)
        #datos_ingreso = lectura_ingreso()
        #datos_salida = lectura_salida()
        #datos_concatenados = procesamiento(datos_ingreso,datos_salida)
        id3 = cargar_tt()
        saldos = [int(id3),referencia,color,talla,cantidad,valor_t,valor_u]
        c.cargar_finales(saldos)


    return render_template('Inventario.html')


@app.route('/salidas', methods=['GET', 'POST'])
def salida():
    if request.method == 'POST':
        talla = request.form.get('talla')
        referencia = request.form.get('referencia')
        color = request.form.get('color')
        cantidad = request.form.get('cantidad')
        valor_u =  request.form.get('valoru')

        ID2 = acutualizar_salida()
        c = Aplicativo()
        sql2 = c.cargar_datos_salida(talla,referencia,color,cantidad,valor_u)
        c.cargar_salida(sql2,ID2)


        valor_t = int(cantidad) * int(valor_u)
        cantidad = int(cantidad) * -1

        #datos_ingreso = lectura_ingreso()
        #datos_salida = lectura_salida()
        #data_salida_concat = procesamiento(datos_ingreso,datos_salida)
        id3 = cargar_tt()
        saldos =  [int(id3),referencia,color,talla,int(cantidad),int(valor_t),int(valor_u)]
        c.cargar_finales(saldos)


    return render_template('Salidas.html')

@app.route('/reporte', methods=['GET', 'POST'])
def reporte():
    db_saldos = pymysql.connect(host='127.0.0.1', user='root', passwd='nora.566', db='referencias', port=3306, charset='utf8')
    cl2 = db_saldos.cursor()
    dato_salida = "select * from saldos"
    cl2.execute(dato_salida)
    saldos = cl2.fetchall()
    db_saldos.commit()
    cl2.close()
    db_saldos.close()
    datos_saldos =  pd.DataFrame(saldos)
    datos_saldos.columns = ['ID','referencia','color','talla','cantidad','valor_total','valor_unitario']
    datos_saldos.drop([0],inplace=True)
    datos_saldos['cantidad'] = datos_saldos['cantidad'].astype(int)
    datos_saldos['talla'] =  datos_saldos['talla'].astype(int)
    datos_saldos['valor_total'] = datos_saldos['valor_total'].astype(int)
    datos_saldos['valor_unitario'] = datos_saldos['valor_unitario'].astype(int)
    datos_pivote =  datos_saldos[[ 'referencia','color','talla','cantidad']]
    datos_pivote = datos_pivote.pivot_table(index = ['referencia','talla',],columns= ['color'], aggfunc=['sum'])
    datos_pivote = datos_pivote.fillna('')
    datos_pivote2 = datos_pivote.reset_index()
    print(datos_pivote2)



    return render_template('reporte.html',tables = [datos_pivote.to_html(classes='data')],titles = ['na','Existencias de inventario'])




if __name__ == '__main__':
    app.run(debug=True)

