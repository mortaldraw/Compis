from __future__ import print_function
import Utils
import TablaVariables
import operator
import copy


class Memoria:
    OFFSET_INICIO_GLOBALES = 1000

    ESPACIO_GLOBALES = 1000
    OFFSET_ENTEROS_GLOBALES = OFFSET_INICIO_GLOBALES
    OFFSET_FLOTANTES_GLOBALES = OFFSET_ENTEROS_GLOBALES + ESPACIO_GLOBALES
    OFFSET_STRINGS_GLOBALES = OFFSET_FLOTANTES_GLOBALES + ESPACIO_GLOBALES

    ESPACIO_TEMPORALES = 1000
    OFFSET_ENTEROS_TEMPORALES = OFFSET_STRINGS_GLOBALES + ESPACIO_GLOBALES
    OFFSET_FLOTANTES_TEMPORALES = OFFSET_ENTEROS_TEMPORALES + ESPACIO_TEMPORALES
    OFFSET_STRINGS_TEMPORALES = OFFSET_FLOTANTES_TEMPORALES + ESPACIO_TEMPORALES

    ESPACIO_LOCALES = 1000
    OFFSET_ENTEROS_LOCALES = OFFSET_STRINGS_TEMPORALES + ESPACIO_TEMPORALES
    OFFSET_FLOTANTES_LOCALES = OFFSET_ENTEROS_LOCALES + ESPACIO_LOCALES
    OFFSET_STRINGS_LOCALES = OFFSET_FLOTANTES_LOCALES + ESPACIO_LOCALES

    ESPACIO_CONSTANTES = 1000
    OFFSET_ENTEROS_CONSTANTES = OFFSET_STRINGS_LOCALES + ESPACIO_LOCALES
    OFFSET_FLOTANTES_CONSTANTES = OFFSET_ENTEROS_CONSTANTES + ESPACIO_CONSTANTES
    OFFSET_STRINGS_CONSTANTES = OFFSET_FLOTANTES_CONSTANTES + ESPACIO_CONSTANTES

    class __Memoria:
        def __init__(self):
            self.__bloque_global = [[], [], []]
            self.__bloque_temporal = [[], [], []]
            self.__bloque_local = [[], [], []]
            self.__bloque_constantes_ejecucion = [[], [], []]
            self.__bloque_constantes_compilacion = {}
            self.__contadores_globales = [0, 0, 0]
            self.__contadores_temporales = [0, 0, 0]
            self.__contadores_locales = [0, 0, 0]
            self.__contadores_constantes = [0, 0, 0]
            self.__pila_offsets_temporales = []
            self.__offsets_temporales = [0, 0, 0]

        def crear_o_buscar_constante(self, constante):
            if constante not in self.__bloque_constantes_compilacion:
                self.__bloque_constantes_compilacion.add(constante)
            return constante

        def getValorConstanteTests(self, espacio):
            for k, v in self.__bloque_constantes_compilacion.items():
                if v == espacio:
                    return k

        def generaEspacioConstantes(self, tipo, valor):
            llave_de_constante = str(tipo.value) + "_" + str(valor)
            if llave_de_constante not in self.__bloque_constantes_compilacion:
                espacio_de_memoria = Memoria.OFFSET_ENTEROS_CONSTANTES + tipo.value * Memoria.ESPACIO_CONSTANTES + \
                                     self.__contadores_constantes[tipo.value]
                self.__bloque_constantes_compilacion.update({llave_de_constante: espacio_de_memoria})
                self.__contadores_constantes[tipo.value] += 1
            return self.__bloque_constantes_compilacion[llave_de_constante]

        def generaEspacioVariablesLocales(self, tipo, lista_dimensiones):
            if Utils.DEBUGGING_MODE:
                print(tipo)
                print("Contadores locales", self.__contadores_locales)
            espacio = Memoria.OFFSET_ENTEROS_LOCALES + self.__contadores_locales[
                tipo.value] + Memoria.ESPACIO_LOCALES * tipo.value
            contador_dimensiones = 1
            if lista_dimensiones is not None:
                for dimension in lista_dimensiones:
                    contador_dimensiones *= dimension
            self.__contadores_locales[tipo.value] += contador_dimensiones
            if Utils.DEBUGGING_MODE:
                print("Espacio:", espacio, "\n____________________________")
            return espacio

        def generaEspacioVariablesGlobales(self, tipo, lista_dimensiones):
            espacio = Memoria.OFFSET_ENTEROS_GLOBALES + self.__contadores_globales[
                tipo.value] + Memoria.ESPACIO_GLOBALES * tipo.value
            contador_dimensiones = 1
            if lista_dimensiones is not None:
                for dimension in lista_dimensiones:
                    contador_dimensiones *= dimension
            self.__contadores_globales[tipo.value] += contador_dimensiones
            if Utils.DEBUGGING_MODE:
                print("Espacio:", espacio, "\n____________________________")
            return espacio

        def generaEspacioTemporal(self, tipo):
            if Utils.DEBUGGING_MODE:
                print(tipo)
                print("Contadores locales", self.__contadores_locales)
            espacio = Memoria.OFFSET_ENTEROS_TEMPORALES + self.__contadores_temporales[
                tipo.value] + Memoria.ESPACIO_TEMPORALES * tipo.value
            self.__contadores_temporales[tipo.value] += 1
            if Utils.DEBUGGING_MODE:
                print("Espacio:", espacio, "\n____________________________")
            return espacio

        def generaEspacioVariable(self, scope, tipo, lista_dimensiones):
            if int(scope) != 0:
                return self.generaEspacioVariablesLocales(tipo, lista_dimensiones)
            return self.generaEspacioVariablesGlobales(tipo, lista_dimensiones)

        def reseteaEspacios(self):
            self.__contadores_locales = [0, 0, 0]
            self.__contadores_temporales = [0, 0, 0]

        def generaEspaciosParaGlobales(self, lista_globales):
            for k, gl in lista_globales.items():
                name = k[k.index('_') + 1:]
                dim = TablaVariables.TablaVariables.getInstance().getVariable(name).getDimensiones()
                if len(dim) > 0:
                    for x in range(0, dim[-1]):
                        self.__bloque_global[gl.getTipo().value].insert(0, Utils.Tipo.getDefault(gl.getTipo()))
                else:
                    self.__bloque_global[gl.getTipo().value].insert(0, Utils.Tipo.getDefault(gl.getTipo()))

        def printVariablesActuales(self):
            print("Globales:")
            print("Enteros:")
            for i in self.__bloque_global[0]:
                print(i)
            print("Flotantes:")
            for i in self.__bloque_global[1]:
                print(i)
            print("Strings:")
            for i in self.__bloque_global[2]:
                print(i)
            print("Constantes compilacion:")
            print(self.__bloque_constantes_compilacion)
            print("Constantes ejecucion:")
            print(self.__bloque_constantes_ejecucion)

            print("Locales:")
            print("Enteros:", len(self.__bloque_local[0]))
            for i in self.__bloque_local[0]:
                print(i)
            print("Flotantes:", len(self.__bloque_local[1]))
            for i in self.__bloque_local[1]:
                print(i)
            print("Strings:", len(self.__bloque_local[2]))
            for i in self.__bloque_local[2]:
                print(i)

        def generaEspaciosParaConstantes(self):
            constantes_ordenadas = sorted(self.__bloque_constantes_compilacion.items(), key=operator.itemgetter(1))
            for k, _ in constantes_ordenadas:
                tipo = int(k[0])
                valor = k[2:]
                if tipo == Utils.Tipo.Entero.value:
                    valor = int(valor)
                if tipo == Utils.Tipo.Flotante.value:
                    valor = float(valor)
                if tipo == Utils.Tipo.String.value:
                    valor = valor[1:-1]
                self.__bloque_constantes_ejecucion[tipo].append(valor)

        def getValorParaEspacio(self, espacio, offset_actual_locales):
            if Utils.DEBUGGING_MODE:
                print("Get de espacio:", espacio)
            while isinstance(espacio, list):
                espacio = self.getValorParaEspacio(espacio[0], offset_actual_locales)
                if Utils.DEBUGGING_MODE:
                    print(Utils.bcolors.buildInfoMessage("Espacio nuevo:" + str(espacio)))

            if espacio < Memoria.OFFSET_ENTEROS_TEMPORALES:
                # Es global
                valor_tipo = (espacio - Memoria.OFFSET_ENTEROS_GLOBALES) / Memoria.ESPACIO_GLOBALES
                indice = (espacio - Memoria.OFFSET_ENTEROS_GLOBALES) % Memoria.ESPACIO_GLOBALES
                if Utils.DEBUGGING_MODE:
                    print(Utils.bcolors.buildSuccessMessage("Get de global:"))
                    print(Utils.bcolors.buildSuccessMessage("\tValor:" + str(self.__bloque_global[valor_tipo][indice])))
                    print(Utils.bcolors.buildSuccessMessage("\tEspacio:" + str(espacio)))
                return self.__bloque_global[valor_tipo][indice]

            if espacio >= Memoria.OFFSET_ENTEROS_CONSTANTES:
                # Es constante
                valor_tipo = (espacio - Memoria.OFFSET_ENTEROS_CONSTANTES) / Memoria.ESPACIO_CONSTANTES
                indice = (espacio - Memoria.OFFSET_ENTEROS_CONSTANTES) % Memoria.ESPACIO_CONSTANTES
                if Utils.DEBUGGING_MODE:
                    print("Get de constante:")
                    print("\tValor:", self.__bloque_constantes_ejecucion[valor_tipo][indice])
                    print("\tEspacio:", espacio)
                return self.__bloque_constantes_ejecucion[valor_tipo][indice]

            if Memoria.OFFSET_ENTEROS_LOCALES <= espacio < Memoria.OFFSET_STRINGS_LOCALES + Memoria.ESPACIO_LOCALES:
                # Es local
                valor_tipo = (espacio - Memoria.OFFSET_ENTEROS_LOCALES) / Memoria.ESPACIO_LOCALES
                indice = (espacio - Memoria.OFFSET_ENTEROS_LOCALES) % Memoria.ESPACIO_LOCALES
                if offset_actual_locales is not None and len(offset_actual_locales) > 0:
                    if Utils.DEBUGGING_MODE:
                        print("Get de local:")
                        print("\tValor:", self.__bloque_local[valor_tipo][indice + offset_actual_locales[valor_tipo]])
                        print("\tEspacio:", espacio)
                        print("\tOffsets:", offset_actual_locales)
                    return self.__bloque_local[valor_tipo][indice + offset_actual_locales[valor_tipo]]
                if Utils.DEBUGGING_MODE:
                    print("Get de local:")
                    print("\tValor:", self.__bloque_local[valor_tipo][indice])
                    print("\tEspacio:", espacio)
                    print("\tOffsets:", offset_actual_locales)
                return self.__bloque_local[valor_tipo][indice]

            # Es temporal
            if Memoria.OFFSET_ENTEROS_TEMPORALES <= espacio < Memoria.OFFSET_STRINGS_TEMPORALES + \
                    Memoria.ESPACIO_TEMPORALES:
                valor_tipo = (espacio - Memoria.OFFSET_ENTEROS_TEMPORALES) / Memoria.ESPACIO_TEMPORALES
                indice = (espacio - Memoria.OFFSET_ENTEROS_TEMPORALES) % Memoria.ESPACIO_TEMPORALES
                if Utils.DEBUGGING_MODE:
                    print("Valor tipo:", valor_tipo)
                    print("Indice:", indice)
                    print(self.__bloque_temporal)
                    print("Offsets: ", self.__offsets_temporales)
                if len(self.__pila_offsets_temporales) > 0:
                    return self.__bloque_temporal[valor_tipo][
                        indice + self.__pila_offsets_temporales[-1][valor_tipo]]
                return self.__bloque_temporal[valor_tipo][indice]

        def setValorParaEspacio(self, espacio, valor, offset_actual_locales=None):
            """
            Funcion que se encarga de asignar valores a los espacios de memoria.
            :param espacio: El espacio de memoria al que se le quiere asignar un valor
            :param valor: Valor a asignar en el espacio de memoria
            :param offset_actual_locales: Offsets utilizados para manejar las variables locales
            :return: Nada.
            """
            while isinstance(espacio, list):
                espacio = self.getValorParaEspacio(espacio[0], offset_actual_locales)

            if Memoria.OFFSET_ENTEROS_GLOBALES <= espacio < Memoria.OFFSET_STRINGS_GLOBALES + Memoria.ESPACIO_GLOBALES:
                # Es global
                valor_tipo = (espacio - Memoria.OFFSET_ENTEROS_GLOBALES) / Memoria.ESPACIO_GLOBALES
                indice = (espacio - Memoria.OFFSET_ENTEROS_GLOBALES) % Memoria.ESPACIO_GLOBALES
                if Utils.DEBUGGING_MODE:
                    print("Set de global:")
                    print("\tValor:", valor)
                    print("\tEspacio:", espacio)
                    print(espacio, indice, valor_tipo)
                self.__bloque_global[valor_tipo][indice] = valor

            # Manejo de locales
            if Memoria.OFFSET_ENTEROS_LOCALES <= espacio < Memoria.OFFSET_STRINGS_LOCALES + Memoria.ESPACIO_LOCALES:
                valor_tipo = (espacio - Memoria.OFFSET_ENTEROS_LOCALES) / Memoria.ESPACIO_LOCALES
                indice = (espacio - Memoria.OFFSET_ENTEROS_LOCALES) % Memoria.ESPACIO_LOCALES

                if len(offset_actual_locales) > 0:
                    self.__bloque_local[valor_tipo][indice + offset_actual_locales[valor_tipo]] = valor
                else:
                    self.__bloque_local[valor_tipo][indice] = valor
                if Utils.DEBUGGING_MODE:
                    print("______________Set a variable local_____________")
                    print(offset_actual_locales)
                    print(self.__bloque_local)
                    print("_______________________________________________")

            # Aqui se manejan los temporales
            if Memoria.OFFSET_ENTEROS_TEMPORALES <= espacio < Memoria.OFFSET_STRINGS_TEMPORALES + \
                    Memoria.ESPACIO_TEMPORALES:
                valor_tipo = (espacio - Memoria.OFFSET_ENTEROS_TEMPORALES) / Memoria.ESPACIO_TEMPORALES
                indice = (espacio - Memoria.OFFSET_ENTEROS_TEMPORALES) % Memoria.ESPACIO_TEMPORALES

                if Utils.DEBUGGING_MODE:
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                    print(self.__offsets_temporales)
                    print(self.__bloque_temporal)
                    print("Pila de offsets", self.__pila_offsets_temporales)
                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

                if len(self.__pila_offsets_temporales) > 0:
                    t = self.__pila_offsets_temporales[-1][valor_tipo]
                    # TODO: hacer este mismo parche para locales y globales, es necesario para que funcionen arreglos.
                    while len(self.__bloque_temporal[valor_tipo]) - t <= indice:
                        self.__bloque_temporal[valor_tipo].append(valor)
                        self.__offsets_temporales[valor_tipo] += 1
                    else:
                        self.__bloque_temporal[valor_tipo][indice + t] = valor
                else:
                    # PARCHE para que funcionen condiciones if/else
                    while len(self.__bloque_temporal[valor_tipo]) <= indice:
                        self.__bloque_temporal[valor_tipo].append(valor)
                        self.__offsets_temporales[valor_tipo] += 1
                    else:
                        self.__bloque_temporal[valor_tipo][indice] = valor
                if Utils.DEBUGGING_MODE:
                    print("__________________TEMPORALES___________________")
                    print(self.__offsets_temporales)
                    print(self.__bloque_temporal)
                    print("Pila de offsets", self.__pila_offsets_temporales)
                    print("_______________________________________________")

        def darDeAltaLocales(self, variables):
            if Utils.DEBUGGING_MODE:
                print(Utils.bcolors.buildInfoMessage("Dando de alta variables locales"))
                print(variables)
                print(self.__bloque_local)
                for k, v in variables.items():
                    print(k, v.getEspacioMemoria())
            cantidad_anterior = copy.deepcopy(self.__bloque_local)
            # Iterar sobre todas las variables recibidas
            for k, v in variables.items():
                # Obtener las dimensiones de la variable
                dim = v.getDimensiones()
                if len(dim) > 0:
                    # Agregar valor default N veces a la lista
                    self.__bloque_local[v.getTipo().value].extend([Utils.Tipo.getDefault(v.getTipo())] * dim[-1])
                else:
                    # Agregar un solo valor
                    self.__bloque_local[v.getTipo().value].append(Utils.Tipo.getDefault(v.getTipo()))
            if Utils.DEBUGGING_MODE:
                print(Utils.bcolors.buildWarningMessage("bloque_local:"))
                print(Utils.bcolors.buildWarningMessage(str(cantidad_anterior)))
                print(Utils.bcolors.buildWarningMessage(str(self.__bloque_local)))
            return [len(x) - len(y) for x, y in zip(self.__bloque_local, cantidad_anterior)]

        def liberarLocales(self, cantidades):
            counter = 0
            if len(self.__pila_offsets_temporales) > 0:
                if Utils.DEBUGGING_MODE:
                    print("_________________________________")
                    print("Liberacion de offsets temporales")
                    print("Pila de offsets", self.__pila_offsets_temporales)
                offsets_de_padre = self.__pila_offsets_temporales.pop()

                diferencias_de_offsets = [x - y for x, y in zip(self.__offsets_temporales, offsets_de_padre)]
                while counter < 3:
                    for i in range(0, diferencias_de_offsets[counter]):
                        self.__bloque_temporal[counter].pop()
                    counter += 1
                self.__offsets_temporales = offsets_de_padre
            counter = 0
            if len(cantidades) > 0:
                while counter < 3:
                    for i in range(0, cantidades[counter]):
                        self.__bloque_local[counter].pop()
                    counter += 1

            if Utils.DEBUGGING_MODE:
                print("Bloque local:", self.__bloque_local)
                print("Bloque temporal:", self.__bloque_temporal)
                print("Offsets temporales:", self.__offsets_temporales)

        def congelarTemporalesParaNuevaFuncion(self):
            self.__pila_offsets_temporales.append(self.__offsets_temporales[:])

    instancia = None

    @staticmethod
    def getInstance():
        if not Memoria.instancia:
            Memoria.instancia = Memoria.__Memoria()
        return Memoria.instancia
