# -*- encoding: utf-8 -*-
##############################################################################
#
#    Avanzosc - Avanced Open Source Consulting
#    Copyright (C) 2011 - 2014 Avanzosc <http://www.avanzosc.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp.osv import orm, fields
import calendar
import datetime
import os
from subprocess import call
import base64
import codecs
# import unicode


class HrEmployeeCalendar(orm.Model):

    _name = 'hr.employee.calendar'
    _description = 'Employee Calendar'

    _columns = {
        # Empleado
        'employee_id':
            fields.many2one('hr.employee', 'Employee', ondelete='cascade'),
        # Año
        'year': fields.integer('Year', required=True),
        # Motivo Festivo
        'name': fields.char('Description', size=64, required=True),
        # Calendario
        'estimated_calendar_resources_ids':
            fields.one2many('estimated.calendar.resources',
                            'hr_employee_calendar_id',
                            'Estimated Calendar Resources'),
    }

    def button_print_calendar(self, cr, uid, ids, *args):
        calendar_pdf_obj = self.pool['show.calendar.pdf']
        # Leo el Objeto Coste
        employee_calendar = self.browse(cr, uid, ids[0])
        # Genero el calendario para el año
        myCalendar = self._generate_calendar(
            cr, uid, employee_calendar.year,
            employee_calendar.employee_id.name)
        # Trato el calendario del Empleado
        for calen in employee_calendar.estimated_calendar_resources_ids:
            if calen.hours == 0 or calen.background_color:
                # Calculo las posiciones en la que se encuentra cada mes
                pos_enero = myCalendar.find('ENERO')
                pos_febrero = myCalendar.find('FEBRERO')
                pos_marzo = myCalendar.find('MARZO')
                pos_abril = myCalendar.find('ABRIL')
                pos_mayo = myCalendar.find('MAYO')
                pos_junio = myCalendar.find('JUNIO')
                pos_julio = myCalendar.find('JULIO')
                pos_agosto = myCalendar.find('AGOSTO')
                pos_septiembre = myCalendar.find('SEPTIEMBRE')
                pos_octubre = myCalendar.find('OCTUBRE')
                pos_noviembre = myCalendar.find('NOVIEMBRE')
                pos_diciembre = myCalendar.find('DICIEMBRE')

                myDate = datetime.datetime.strptime(calen.date, '%Y-%m-%d')
                myMonth = int(myDate.strftime('%m'))
                myDay = int(myDate.strftime('%d'))
                posDesde = 0
                posHasta = 0

                if myMonth == 1:
                    posDesde = pos_enero
                    posHasta = pos_febrero
                if myMonth == 2:
                    posDesde = pos_febrero
                    posHasta = pos_marzo
                if myMonth == 3:
                    posDesde = pos_marzo
                    posHasta = pos_abril
                if myMonth == 4:
                    posDesde = pos_abril
                    posHasta = pos_mayo
                if myMonth == 5:
                    posDesde = pos_mayo
                    posHasta = pos_junio
                if myMonth == 6:
                    posDesde = pos_junio
                    posHasta = pos_julio
                if myMonth == 7:
                    posDesde = pos_julio
                    posHasta = pos_agosto
                if myMonth == 8:
                    posDesde = pos_agosto
                    posHasta = pos_septiembre
                if myMonth == 9:
                    posDesde = pos_septiembre
                    posHasta = pos_octubre
                if myMonth == 10:
                    posDesde = pos_octubre
                    posHasta = pos_noviembre
                if myMonth == 11:
                    posDesde = pos_noviembre
                    posHasta = pos_diciembre
                if myMonth == 12:
                    posDesde = pos_diciembre
                    posHasta = 0

                if myDay == 1:
                    dia = '1'
                if myDay == 2:
                    dia = '2'
                if myDay == 3:
                    dia = '3'
                if myDay == 4:
                    dia = '4'
                if myDay == 5:
                    dia = '5'
                if myDay == 6:
                    dia = '6'
                if myDay == 7:
                    dia = '7'
                if myDay == 8:
                    dia = '8'
                if myDay == 9:
                    dia = '9'
                if myDay > 9:
                    dia = str(myDay)
                # Realizo los cambios
                if posDesde > 0 and posHasta > 0:
                    if calen.hours == 0 and calen.background_color:
                        if calen.background_color != 'None':
                            viejo = ('bgcolor="White" align="right"><font ' +
                                     'color="blue">' + dia + '<')
                            nuevo = ('bgcolor="' +
                                     str(calen.background_color) +
                                     '" align="right"><font color="red">' +
                                     dia + '<')
                            subCal = myCalendar[posDesde:posHasta]
                            myCalendar = (myCalendar[:posDesde] +
                                          subCal.replace(viejo, nuevo) +
                                          myCalendar[posHasta:])
                        else:
                            viejo = ('bgcolor="White" align="right"><font' +
                                     ' color="blue">' + dia + '<')
                            nuevo = ('bgcolor="White" align="right"><font ' +
                                     'color="red">' + dia + '<')
                            subCal = myCalendar[posDesde:posHasta]
                            myCalendar = (myCalendar[:posDesde] +
                                          subCal.replace(viejo, nuevo) +
                                          myCalendar[posHasta:])
                    else:
                        if calen.hours == 0:
                            viejo = ('bgcolor="White" align="right"><font ' +
                                     'color="blue">' + dia + '<')
                            nuevo = ('bgcolor="White" align="right"><font ' +
                                     'color="red">' + dia + '<')
                            subCal = myCalendar[posDesde:posHasta]
                            myCalendar = (myCalendar[:posDesde] +
                                          subCal.replace(viejo, nuevo) +
                                          myCalendar[posHasta:])
                        else:
                            if calen.background_color:
                                if calen.background_color != 'None':
                                    viejo = ('bgcolor="White" align="right"' +
                                             '><font color="blue">' + dia +
                                             '<')
                                    nuevo = ('bgcolor="' +
                                             str(calen.background_color) +
                                             '" align="right"><font color=' +
                                             '"blue">' + dia + '<')
                                    subCal = myCalendar[posDesde:posHasta]
                                    myCalendar = (myCalendar[:posDesde] +
                                                  subCal.replace(viejo, nuevo)
                                                  + myCalendar[posHasta:])
                else:
                    if calen.hours == 0 and calen.background_color:
                        if calen.background_color != 'None':
                            viejo = ('bgcolor="White" align="right"><font ' +
                                     'color="blue">' + dia + '<')
                            nuevo = ('bgcolor="' +
                                     str(calen.background_color) +
                                     '" align="right"><font color="red">' +
                                     dia + '<')
                            subCal = myCalendar[posDesde:]
                            myCalendar = (myCalendar[:posDesde] +
                                          subCal.replace(viejo, nuevo))
                        else:
                            viejo = ('bgcolor="White" align="right"><font ' +
                                     'color="blue">' + dia + '<')
                            nuevo = ('bgcolor="White" align="right"><font ' +
                                     'color="red">' + dia + '<')
                            subCal = myCalendar[posDesde:]
                            myCalendar = (myCalendar[:posDesde] +
                                          subCal.replace(viejo, nuevo))
                    else:
                        if calen.hours == 0:
                            viejo = ('bgcolor="White" align="right"><font ' +
                                     ' color="blue">' + dia + '<')
                            nuevo = ('bgcolor="White" align="right"><font ' +
                                     'color="red">' + dia + '<')
                            subCal = myCalendar[posDesde:]
                            myCalendar = (myCalendar[:posDesde] +
                                          subCal.replace(viejo, nuevo))
                        else:
                            if calen.background_color:
                                if calen.background_color != 'None':
                                    viejo = ('bgcolor="White" align="right"' +
                                             '><font color="blue">' + dia +
                                             '<')
                                    nuevo = ('bgcolor="' +
                                             str(calen.background_color) +
                                             '" align="right"><font color=' +
                                             '"blue">' + dia + '<')
                                    subCal = myCalendar[posDesde:]
                                    myCalendar = (myCalendar[:posDesde] +
                                                  subCal.replace(viejo,
                                                                 nuevo))

        # Genero el PATH para guardar el calendario en formato HTML
        directorioOriginal = os.getcwd()
        myPath = (str(directorioOriginal) + "/openerp/addons/avanzosc_" +
                  "calendar/reports")
        # Me posiciono en el directorio para guardar el documento en formato
        # HTML
        miDirectorio = os.path.join(os.pardir, myPath)
        os.chdir(miDirectorio)
        # Borro el HTML y el PDF viejo que halla quedado de antes
        a = 0
        try:
            os.remove("myCalendar.html")
            os.remove("myCalendar.pdf")
        except:
            a = 1
        # Guardo html
        f = codecs.open('myCalendar.html', "w", encoding='utf-8')
        f.write(myCalendar)
        f.close()
        # Realizo la conversion de HTML  a PDF
        call(["wkhtmltopdf", "myCalendar.html", "myCalendar.pdf"])
        # Leo el PDF Generado en binario
        pdf_file = open('myCalendar.pdf', "rb")
        pdf_binary = base64.encodestring(pdf_file.read())
        # Llamo al wizard de pdf generado, creando un registro
        result_id = calendar_pdf_obj.create(
            cr, uid, {'pdfcalendar': pdf_binary})
        # Vuelvo al Directorio Original
        os.chdir(directorioOriginal)
        return {'type': 'ir.actions.act_window',
                'res_model': 'show.calendar.pdf',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_id': result_id,
                }

    def _generate_calendar(self, cr, uid, year, name):
        # Genero el Calendario
        # myCal = calendar.HTMLCalendar(calendar.MONDAY)
        myCal = calendar.LocaleHTMLCalendar(calendar.MONDAY, 'en_US.UTF-8')
        myCalendar = myCal.formatyear(year, 3)
        # Meto el meta
        myCalendar2 = ('<meta http-equiv="Content-Type" content="text/html;' +
                       'charset=UTF-8">' + myCalendar)
        myCalendar = myCalendar2
        myCalendar = myCalendar.replace(str(year), name + ' - CALENDAR: ' +
                                        str(year))
        # Cambio cosas del calendario
        myCalendar = myCalendar.replace('January', 'ENERO')
        myCalendar = myCalendar.replace('February', 'FEBRERO')
        myCalendar = myCalendar.replace('March', 'MARZO')
        myCalendar = myCalendar.replace('April', 'ABRIL')
        myCalendar = myCalendar.replace('May', 'MAYO')
        myCalendar = myCalendar.replace('June', 'JUNIO')
        myCalendar = myCalendar.replace('July', 'JULIO')
        myCalendar = myCalendar.replace('August', 'AGOSTO')
        myCalendar = myCalendar.replace('September', 'SEPTIEMBRE')
        myCalendar = myCalendar.replace('October', 'OCTUBRE')
        myCalendar = myCalendar.replace('November', 'NOVIEMBRE')
        myCalendar = myCalendar.replace('December', 'DICIEMBRE')

        myCalendar = myCalendar.replace('Mon', 'Lun')
        myCalendar = myCalendar.replace('Tue', 'Mar')
        myCalendar = myCalendar.replace('Wed', 'Mie')
        myCalendar = myCalendar.replace('Thu', 'Jue')
        myCalendar = myCalendar.replace('Fri', 'Vie')
        myCalendar = myCalendar.replace('Sat', 'Sab')
        myCalendar = myCalendar.replace('Sun', 'Dom')
        # Pongo color blanco a las celdas de la tabla
        myCalendar = myCalendar.replace('td class', 'td valign="top" bgcolor='
                                        '"White" class')
        # Quito las clases
        myCalendar = myCalendar.replace('class="mon"', '')
        myCalendar = myCalendar.replace('class="tue"', '')
        myCalendar = myCalendar.replace('class="wed"', '')
        myCalendar = myCalendar.replace('class="thu"', '')
        myCalendar = myCalendar.replace('class="fri"', '')
        myCalendar = myCalendar.replace('class="sat"', '')
        myCalendar = myCalendar.replace('class="sun"', '')
        # Cambio la alineacion
        myCalendar = myCalendar.replace('<td>', '<td valign="top">')
        # Pongo en Azul los días del calendario
        myCalendar = myCalendar.replace('>1<', 'align="right"><font color='
                                        '"blue">1</font><')
        myCalendar = myCalendar.replace('>2<', 'align="right"><font color='
                                        '"blue">2</font><')
        myCalendar = myCalendar.replace('>3<', 'align="right"><font color='
                                        '"blue">3</font><')
        myCalendar = myCalendar.replace('>4<', 'align="right"><font color='
                                        '"blue">4</font><')
        myCalendar = myCalendar.replace('>5<', 'align="right"><font color='
                                        '"blue">5</font><')
        myCalendar = myCalendar.replace('>6<', 'align="right"><font color='
                                        '"blue">6</font><')
        myCalendar = myCalendar.replace('>7<', 'align="right"><font color='
                                        '"blue">7</font><')
        myCalendar = myCalendar.replace('>8<', 'align="right"><font color='
                                        '"blue">8</font><')
        myCalendar = myCalendar.replace('>9<', 'align="right"><font color='
                                        '"blue">9</font><')
        myCalendar = myCalendar.replace('>10<', 'align="right"><font color='
                                        '"blue">10</font><')
        myCalendar = myCalendar.replace('>11<', 'align="right"><font color='
                                        '"blue">11</font><')
        myCalendar = myCalendar.replace('>12<', 'align="right"><font color='
                                        '"blue">12</font><')
        myCalendar = myCalendar.replace('>13<', 'align="right"><font color='
                                        '"blue">13</font><')
        myCalendar = myCalendar.replace('>14<', 'align="right"><font color='
                                        '"blue">14</font><')
        myCalendar = myCalendar.replace('>15<', 'align="right"><font color='
                                        '"blue">15</font><')
        myCalendar = myCalendar.replace('>16<', 'align="right"><font color='
                                        '"blue">16</font><')
        myCalendar = myCalendar.replace('>17<', 'align="right"><font color='
                                        '"blue">17</font><')
        myCalendar = myCalendar.replace('>18<', 'align="right"><font color='
                                        '"blue">18</font><')
        myCalendar = myCalendar.replace('>19<', 'align="right"><font color='
                                        '"blue">19</font><')
        myCalendar = myCalendar.replace('>20<', 'align="right"><font color='
                                        '"blue">20</font><')
        myCalendar = myCalendar.replace('>21<', 'align="right"><font color='
                                        '"blue">21</font><')
        myCalendar = myCalendar.replace('>22<', 'align="right"><font color='
                                        '"blue">22</font><')
        myCalendar = myCalendar.replace('>23<', 'align="right"><font color='
                                        '"blue">23</font><')
        myCalendar = myCalendar.replace('>24<', 'align="right"><font color='
                                        '"blue">24</font><')
        myCalendar = myCalendar.replace('>25<', 'align="right"><font color='
                                        '"blue">25</font><')
        myCalendar = myCalendar.replace('>26<', 'align="right"><font color='
                                        '"blue">26</font><')
        myCalendar = myCalendar.replace('>27<', 'align="right"><font color='
                                        '"blue">27</font><')
        myCalendar = myCalendar.replace('>28<', 'align="right"><font color='
                                        '"blue">28</font><')
        myCalendar = myCalendar.replace('>29<', 'align="right"><font color='
                                        '"blue">29</font><')
        myCalendar = myCalendar.replace('>30<', 'align="right"><font color='
                                        '"blue">30</font><')
        myCalendar = myCalendar.replace('>31<', 'align="right"><font color='
                                        '"blue">31</font><')
        # Pongo separacion entre los meses
        myCalendar = myCalendar.replace('</td><td valign="top"><table',
                                        '</td><td width="10px"></td><td '
                                        'valign="top"><table')
        return myCalendar
