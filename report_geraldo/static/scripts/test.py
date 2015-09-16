from geraldo import Report, ReportBand, DetailBand, SystemField, Label, ObjectValue
from geraldo.utils import cm

family = [
    {'name': 'Leticia', 'age': 29, 'weight': 55.7, 'genre': 'female', 'status': 'parent'},
    {'name': 'Marinho', 'age': 28, 'weight': 76, 'genre': 'male', 'status': 'parent'},
    {'name': 'Tarsila', 'age': 4, 'weight': 16.2, 'genre': 'female', 'status': 'child'},
    {'name': 'Linus', 'age': 0, 'weight': 1.5, 'genre': 'male', 'status': 'child'},
    {'name': 'Mychelle', 'age': 19, 'weight': 50, 'genre': 'female', 'status': 'nephew'},
    {'name': 'Mychell', 'age': 17, 'weight': 55, 'genre': 'male', 'status': 'niece'},
]

class MyFamilyReport(Report):
    class band_detail(DetailBand):
        height = 0.7*cm
        elements = [
            Label(text='Name'),
            ObjectValue(expression='name', left=1.5*cm),
        ]
        borders = {'bottom': True}
        
        
from geraldo.generators import PDFGenerator

my_report = MyFamilyReport(queryset=family)
my_report.generate_by(PDFGenerator, filename='family.pdf')