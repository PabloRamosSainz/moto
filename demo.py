# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#from dwave.system import LeapHybridSampler # Este dwave o el de abajo mas avanzado
from dwave.system import DWaveSampler, EmbeddingComposite

from dimod import BinaryQuadraticModel

numero_velocidades = [0,1,2,3]  #  Cada tramo con diferentes velocidades. Da las filas  de los datos
tramos = [0,1,2]   # Numero de tramos con iguales datos . Da las columnas de los datos
Velocidad = [[70, 70, 70],
	       [80, 80, 80],
           [90, 90, 90],
           [100, 100, 100]]     #  Velocidad por tramo y distancia
d_max = [[225, 225, 225],
	       [200, 200, 200],
           [175, 175, 175],
           [150, 150, 150]] #  Distancia maximas que depende de la velocidad
distancia = [[100, 150, 200],
	       [100, 150, 200],
           [100, 150, 200],
           [100, 150, 200]] #  Distancia de cada tramo
Tiempo_v = [[1.4, 2.1, 2.9],
	       [1.3, 1.9, 2.5],
           [1.1, 1.7, 2.2],
           [1, 1.5, 2]] #  tiempo de viaje
Tiempo_r = [[0.9, 1.3, 1.8],
	       [1, 1.5, 2.3],
           [1.1, 1.7, 2.7],
           [1.3, 2, 3.2]] #  tiempo de recarga
Tiempo_v_r=[[2.3, 3.4, 4.6],
	       [2.3, 3.4, 4.5],
           [2.2, 3.4, 4.5],
           [2.3, 3.45, 4.7]]
distancia_total=400
n_tramos=3
Total_tiempo_v=0
Total_tiempo_r=0
Total_tiempo_v_r=0
Total_distancia=0


    # Build a variable for each pump
x = [[f'C{p}_tramo1',f'C{p}_tramo2',f'C{p}_tramo3']  for p in numero_velocidades]

    # Initialize BQM
bqm = BinaryQuadraticModel('BINARY')

    # Objective
for p in numero_velocidades:
   for t in tramos:
        bqm.add_variable(x[p][t],Tiempo_v_r[p][t])



      # Constraint 1: Solo usar dos tramos y barre en las velocidades y tramos
for p in numero_velocidades:
    c1 = [(x[p][t], 1) for t in tramos for p in numero_velocidades]
    bqm.add_linear_inequality_constraint(c1,
            constant=0,
            lb =n_tramos,
            ub =n_tramos,
            lagrange_multiplier = 120,
            label = 'c1_pump_'+str(p))

 # Constraint 3: Ajusto a la distancia
for t in tramos:
         c2 = [(x[p][t], distancia[p][t])  for p in numero_velocidades for t in tramos]
         bqm.add_linear_inequality_constraint(c2,
                 constant = -distancia_total,
                 lb=0,
                 ub=0,
                 lagrange_multiplier =1,
                 label = 'c3_tramos_'+str(t))

    # Run on hybrid sampler
print("\nRunning hybrid solver...")

#sampler = LeapHybridSampler()
#sampleset = sampler.sample(bqm)
    
sampler = EmbeddingComposite(DWaveSampler())                  # Avanzado
sampleset = sampler.sample(bqm,num_reads=1000,label='Example')

print (sampleset)

sample=sampleset.first.sample   #ordena por energia de menos a mas. La primera es la de menor energia


 # Print out version slots header
print("\n\ttramos1\ttramos2\ttramos3")
 # Generate printout for each pump's usage
for p in numero_velocidades:
    printout = 'Velociades'+str(p)
    for tramos in range(3):
        printout += "\t" + str(sample[x[p][tramos]])
        Total_tiempo_v += sample[x[p][tramos]] * Tiempo_v[p] [tramos]
        Total_tiempo_r += sample[x[p][tramos]] * Tiempo_r[p] [tramos]
        Total_distancia += sample[x[p][tramos]] * distancia[p] [tramos]
        Total_tiempo_v_r += sample[x[p][tramos]] * Tiempo_v_r[p] [tramos]
    print(printout)

#Print out total _tiempo viaje y recarga information
print("\nTotal distancia (km):\t", Total_distancia)
print("\nTotal tiempo viaje (h):\t", Total_tiempo_v)
print("\nTotal tiempo recarga (h):\t", Total_tiempo_r)
print("Total tiempo viaje+recarga (h):\t", Total_tiempo_v_r, "\n")