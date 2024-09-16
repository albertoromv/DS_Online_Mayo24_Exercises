import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import pearsonr, chi2_contingency, f_oneway
import seaborn as sns
from sklearn.feature_selection import f_regression

#PRIMERA
def funcion_describe(df):

    resultado = pd.DataFrame()
    """
    Obtiene información sobre porcentaje de cardinalidad, el tipo de datos, los valores únicos y el porcentaje de valores NaN en cada columna de un DataFrame.

    Args:
        df: El DataFrame del que se quiere obtener la información.

    Returns:
        Un diccionario con la información de cada columna.
    """
    for col in df.columns:
        datos = {}
        datos['%_cardinalidad'] = round(df[col].nunique() / len(df) * 100, 2)
        datos['Tipo_dato'] = df[col].dtype
        datos['valores_unicos'] = df[col].nunique()
        datos['%_NaN'] = round(df[col].isna().mean() * 100, 2)
        resultado[col] = pd.Series(datos)
    return resultado.transpose()



#SEGUNDA    
def funcion_categorias(df, umbral_categoria, umbral_continua):
    
    """
    Obtiene información sobre el tipo de categoria de cada columna de un DataFrame.

    Args:
        df: El DataFrame del que se quiere obtener la información.

    Returns:
        Un diccionario con la información de cada columna.
    """

    resultado = pd.DataFrame()
    for col in df.columns:
        datos = {}
        if pd.api.types.is_numeric_dtype(df[col]):
            datos['Categoria'] = 'Numerica Discreta' if df[col].nunique() >= umbral_categoria and df[col].nunique() < umbral_continua  else 'Numérica Continua'
            if df[col].nunique() == 2:
                datos['Categoria'] = 'Binaria'
        else:    
            datos['Categoria'] = 'Binaria' if df[col].nunique() == 2 else 'Categorica'
   
        resultado[col] = pd.Series(datos)
    return resultado.transpose()





#TERCERA    
def get_features_num_regression(df, target_col, umbral_corr=0.7, pvalue=None):
    """
    Devuelve dos listas con las columnas numéricas del dataframe que están directa e indirectamente
    correlacionadas con la columna designada por "target_col" según el umbral de correlación especificado.
    Además, se pueden filtrar las columnas por su p-value si se especifica.

    Args:
        df: DataFrame de análisis.
        target_col: Nombre de la columna objetivo.
        umbral_corr: Umbral para considerar una correlación significativa.
        pvalue: Umbral para considerar la significancia estadística de la correlación.

    Returns:
        Dos listas: una con columnas directamente correlacionadas y otra con indirectamente correlacionadas.
    """
    # Asegurarse de que target_col es numérica y está presente en el DataFrame
    if target_col not in df.columns or not pd.api.types.is_numeric_dtype(df[target_col]):
        raise ValueError(f"La columna objetivo '{target_col}' debe ser numérica y estar presente en el DataFrame.")

    # Filtrar columnas numéricas, excluyendo la target
    columnas_num = [col for col in df.columns if col != target_col and pd.api.types.is_numeric_dtype(df[col])]

    # Preparar DataFrame solo con columnas numéricas (incluyendo target_col para cálculo de correlación)
    df_numericas = df[columnas_num + [target_col]]

    # Calcular correlaciones
    correlaciones = df_numericas.corr()[target_col].drop(target_col)
    
    # Opcional: Calcular p-values si se requiere filtrar por significancia
    if pvalue is not None:
        _, p_values = f_regression(df_numericas[columnas_num], df_numericas[target_col])
        # Filtrar columnas por p-value
        columnas_significativas = correlaciones.index[p_values < pvalue].tolist()
        correlaciones = correlaciones[columnas_significativas]

    # Filtrar por umbral de correlación
    directamente_correlacionadas = correlaciones[correlaciones >= umbral_corr].index.tolist()
    indirectamente_correlacionadas = correlaciones[correlaciones <= -umbral_corr].index.tolist()

    print(f"Columnas correlacionadas positivamente: {directamente_correlacionadas}, con correlación de Pearson >= {umbral_corr} y significancia en coeficientes {100*(1-pvalue)}%")
    print(f"Columnas correlacionadas negativamente: {indirectamente_correlacionadas}, con correlación de Pearson <= {umbral_corr} y significancia en coeficientes {100*(1-pvalue)}%")

    return directamente_correlacionadas, indirectamente_correlacionadas




#CUARTA 
def plot_features_num_regression(df, target_col="", columns=[], umbral_corr=0, pvalue=None):
    """
    Crea un conjunto de pair plots para visualizar las correlaciones entre las columnas numéricas del DataFrame.

    Args:
        df: El DataFrame del que se quiere visualizar las correlaciones.
        target_col: El nombre de la columna objetivo.
        umbral_corr= numbral establecido de correlacion con la target
        pvalue: El valor de p-valor.

    Returns:
        None
    """

    columnas_para_pintar = []
    columnas_umbral_mayor = []
    
    if columns == []:
        columns = df.columns

    #iteramos por la columnas
    for col in columns:
        #si en la iteracion de las columnas del DF y siempre que...
        # se comprube si son numéricas(true) o no son numéricas(false)
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            # usando el indice de correlación de Pearson y el p-valor(funcion pearsonr)
            # calculamos dichos parametros para target y resto de columnas
            corr, pv = pearsonr(df[col], df[target_col])
            if abs(corr) > umbral_corr:
                columnas_umbral_mayor.append(col)
                if pvalue is None or pv < pvalue:
                    columnas_para_pintar.append(col)

    # Número máximo de gráficas por grupo
    max_graficas_por_grupo = 5

    # Dividir en grupos según el número máximo de gráficas
    len(columnas_para_pintar) // max_graficas_por_grupo
    # En un alista de comprension, iteramos en rango desde 0 hasta el numero de columnas a pintar, por cada grupo maximo establecido
    # creando graficas con columnas maxi de i+ grupo max establecido ( ejem: '0 hasta 0+6)
    columnas = [columnas_para_pintar[i:i+max_graficas_por_grupo] for i in range(0, len(columnas_para_pintar), max_graficas_por_grupo)]

    # iteramos por i y por valor 'umbral_corr' establecido a cada grupo en cada iteración,  creeando pair plots para cada grupo,
    for i, grupo in enumerate(columnas):
        sns.pairplot(data = df, kind = 'scatter', vars=grupo, hue=target_col)
        plt.suptitle(f"Group {i}", y=1.02)# creo nombres de grupo un poco por encima de y, para que no se superponga con la gráfica
        plt.show()
    
    return f"Las columnas con una correlación de Pearson fuerte y con significancia al {100*(1-pvalue)} en la correlación son", columnas_umbral_mayor




#QUINTA 
def get_features_cat_regression(dataframe: pd.DataFrame, target_col: str, pvalue: float = 0.05) -> list:
    """
    Esta función recibe un dataframe y dos argumentos adicionales: 'target_col' y 'pvalue'.
    
    Parámetros:
    - dataframe: DataFrame de pandas.
    - target_col: Nombre de la columna que actuará como el objetivo para un modelo de regresión.
    - pvalue: Valor de p umbral para la significancia estadística (por defecto es 0.05).
    
    Devuelve:
    - Una lista con las columnas categóricas cuya relación con 'target_col' es estadísticamente significativa.
    - None si hay errores en los parámetros de entrada.
    """
    # Comprueba si 'target_col' es una columna numérica válida en el dataframe
    if target_col not in dataframe.columns or not pd.api.types.is_numeric_dtype(dataframe[target_col]):
        print(f"Error: '{target_col}' no es una columna numérica válida en el dataframe.")
        return None
    
    # Comprueba si 'pvalue' es un float válido
    if not isinstance(pvalue, float):
        print("Error: 'pvalue' debería ser un float.")
        return None
    
    # Identifica las columnas categóricas
    cat_columns = dataframe.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    
    # Comprueba si hay columnas categóricas
    if not cat_columns:
        print("Error: No se encontraron columnas categóricas en el dataframe.")
        return None
    
    # Realiza pruebas estadísticas y filtra columnas basadas en el valor de p
    selected_columns = []
    for cat_col in cat_columns:
        
        if round(dataframe[cat_col].nunique() / len(dataframe) * 100, 2) < 5: # Menos de 5% de cardinalidad considero target numérico discreto
        
            contingency_table = pd.crosstab(dataframe[cat_col], dataframe[target_col])
            _, p, _, _ = chi2_contingency(contingency_table)
        
        else: # El target es numérico continuo
            _, p = f_oneway(*[dataframe[target_col][dataframe[cat_col] == category] for category in dataframe[cat_col].unique()])
        
        if p < pvalue:
            selected_columns.append(cat_col)
    
    return selected_columns



#SEXTA
def plot_features_cat_regression(dataframe: pd.DataFrame, target_col: str = "", 
                                  columns: list = [], pvalue: float = 0.05, 
                                  with_individual_plot: bool = False) -> list:
    """
    Esta función recibe un dataframe y varios argumentos opcionales para visualizar y analizar la relación
    entre variables categóricas y una columna objetivo en un modelo de regresión.

    Parámetros:
    - dataframe: DataFrame de pandas.
    - target_col: Nombre de la columna que actuará como el objetivo para un modelo de regresión.
    - columns: Lista de nombres de columnas categóricas a considerar (por defecto, todas las numéricas).
    - pvalue: Valor de p umbral para la significancia estadística (por defecto es 0.05).
    - with_individual_plot: Booleano que indica si se deben incluir gráficos individuales para cada columna (por defecto es False).

    Devuelve:
    - Una lista con las columnas seleccionadas que cumplen con las condiciones de significancia.
    - None si hay errores en los parámetros de entrada.
    """
    # Comprueba si 'target_col' es una columna numérica válida en el dataframe
    if target_col and (target_col not in dataframe.columns or not pd.api.types.is_numeric_dtype(dataframe[target_col])):
        print(f"Error: '{target_col}' no es una columna numérica válida en el dataframe.")
        return None
    
    # Comprueba si 'pvalue' es un float válido
    if not isinstance(pvalue, float):
        print("Error: 'pvalue' debería ser un float.")
        return None
    
    # Comprueba si 'columns' es una lista válida de strings
    if not isinstance(columns, list) or not all(isinstance(col, str) for col in columns):
        print("Error: 'columns' debería ser una lista de strings.")
        return None
    
    # Comprueba si 'with_individual_plot' es un booleano válido
    if not isinstance(with_individual_plot, bool):
        print("Error: 'with_individual_plot' debería ser un booleano.")
        return None
    
    # Si 'columns' está vacío, utiliza todas las columnas numéricas en el dataframe
    if not columns:
        columns = dataframe.select_dtypes(include=['number']).columns.tolist()
    
    # Filtra columnas basadas en pruebas estadísticas
    selected_columns = get_features_cat_regression(dataframe, target_col, pvalue)
    #selected_columns = list(set(selected_columns) & set(columns))
    
    if not selected_columns:
        print("Ninguna columna cumple con las condiciones especificadas para trazar.")
        return None
    
    if with_individual_plot:
        # Histogramas
        for cat_col in selected_columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(data=dataframe, x=target_col, hue=cat_col, multiple="dodge", kde=True)
            plt.title(f"Histograma para {target_col} por {cat_col}")
            plt.show()
        
        
    else:
        # Histogramas
        for cat_col in selected_columns:
            plt.figure(figsize=(10, 6))
            sns.histplot(data=dataframe, x=target_col, hue=cat_col, multiple="layer", kde=True)
            plt.title(f"Histograma para {target_col} por {cat_col}")
            plt.show()
    
    return selected_columns



