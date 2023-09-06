import os

import pandas as pd
import requests
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_numeric_dtype,
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.session_state.openalex_works = []
st.session_state.candidate_works = []
st.session_state.model = "(All)"

# TODO: Remove this once the pipeline is complete.
# ruff: noqa: E501
st.session_state.references = references = [
    "Abdelal, Rawi, Yoshiko M. Herrera, Alastair Iain Johnston, and Rose McDermott. 2006. “Identity as a Variable.” Perspectives on Politics 4 (4): 695–711.",
    "Alba, Richard, and Victor Nee. 2003. Remaking the American Mainstream: Assimilation and Contemporary Immigration. Cambridge, Mass.: Harvard University Press.",
    "Asad, Asad L., and Jackelyn Hwang. 2019. “Indigenous Places and the Making of Undocumented Status in Mexico-US Migration.” International Migration Review 53 (4): 1032–1077.",
    "Auspurg, Katrin, and Thomas Hinz. 2014. Factorial Survey Experiments, vol. 175. Thousand Oaks, Calif.: Sage.",
    "Bailey, Stanley R. 2008. “Unmixing for Race Making in Brazil.” American Journal of Sociology 114 (3): 577–614.",
    "Bailey, Stanley R., and Fabrício M. Fialho. 2018. “Shifting Racial Subjectivities and",
    "Ideologies in Brazil.” Socius 4. https://doi.org/10.1177/2378023118797550.",
    "Barbary, Olivier, and Regina Martínez Casas. 2015. “L’explosion de l’autodéclaration",
    "Indigène entre les Recensements Mexicains de 2000 et 2010.” Autrepart 74–75 (2): 215.",
    "Barth, Fredrik. 1969. Ethnic Groups and Boundaries: The Social Organization of Cultural Difference. Boston: Little, Brown.",
    "Bonﬁl Batalla, Guillermo. 1996. México Profundo: Reclaiming a Civilization. Austin: University of Texas Press.",
    "Brubaker, Rogers. 2002. “Ethnicity without Groups.” European Journal of Sociology/ Archives européennes de sociologie 43 (2): 163–89.",
    "Brubaker, Rogers. 2004. Ethnicity without Groups. Cambridge, Mass.: Harvard University Press.",
    "Brubaker, Rogers. 2006. Nationalist Politics and Everyday Ethnicity in a Transylvanian Town. Princeton, N.J.: Princeton University Press.",
    "Brubaker, Rogers. 2013. “Categories of Analysis and Categories of Practice: A Note on the Study of Muslims in European Countries of Immigration.” Ethnic and Racial Studies",
    "36 (1): 1–8.",
    "Calhoun, Craig J. 1997. Nationalism. Minneapolis: University of Minnesota Press.",
    "Campos-Vázquez, Raymundo M., and Eduardo M. Medina-Cortina. 2019. “Skin Color and Social Mobility: Evidence from Mexico.” Demography 56 (1): 321–43.",
    "Casanova, Pablo González. (1965) 2003. La democracia en México. Mexico City: Ediciones Era.",
    "Cerulo, Karen A. 1997. “Identity Construction: New Issues, New Directions.” Annual Review of Sociology 23 (1): 385–409.",
    "Cornell, Stephen. 1988. “The Transformations of Tribe: Organization and Self-Concept in Native American Ethnicities.” Ethnic and Racial Studies 11 (1): 27–47.",
    "Corntassel, Jeff. 2003. “Who Is Indigenous? ‘Peoplehood’ and Ethnonationalist Approaches to Rearticulating Indigenous Identity.” Nationalism and Ethnic Politics 9 (1): 75–100. Boundary Crossing",
    "157",
    "De la Cadena, Marisol. 2000. Indigenous Mestizos: The Politics of Race and Culture in",
    "Cuzco, Peru, 1919–1991. Durham, N.C.: Duke University Press.",
    "De la Peña, Guillermo. 1999. “La ciudadanía étnica y la construcción de los ‘indios’ en el México contemporáneo.” In La sociedad civil: De la teoría a la realidad, edited by Alberto J. Olvera. Mexico City: El Colegio de Mexico.",
    "De la Peña, Guillermo. 2006. “A New Mexican Nationalism? Indigenous Rights, Constitutional Reform and the Conﬂicting Meanings of Multiculturalism.” Nations and Nationalism 12 (2): 279–302.",
    "Del Popolo, Fabiana. 2001. Características Socioeconómicas y sociodemográﬁcas de la población en América Latina. Santiago: CEPAL.",
    "Del Popolo, Fabiana, ed. 2017. Los pueblos indígenas en América (Abya Yala): Desafíos para la igualdad en la diversidad. Santiago: CEPAL.",
    "Dirección General de Estadística (1930) 1993. Censo de Población. Mexico City: INEGI.",
    "Eschbach, Karl, Khalil Supple, and C. Matthew Snipp. 1998. “Changes in Racial Identiﬁcation and the Educational Attainment of American Indians, 1970–1990.” Demography 35 (1): 35–43.",
    "Flores, René D., and David Sulmont. 2021. “To Be or Not to Be? Material Incentives and Indigenous Identiﬁcation in Latin America.” Ethnic and Racial Studies 44 (14):",
    "2658–78.",
    "Flores, René D., and Edward Telles. 2012. “Social Stratiﬁcation in Mexico: Disentangling Color, Ethnicity, and Class.” American Sociological Review 77 (3): 486–94.",
    "Friedlander, Judith. 2006. Being Indian in Hueyapan: A Revised and Updated Edition. Dordrecht: Springer.",
    "Gans, Herbert J. 1979. “Symbolic Ethnicity: The Future of Ethnic Groups and Cultures in America.” Ethnic and Racial Studies 2 (1): 1–20.",
    "Gelman, Andrew, and Jennifer Hill. 2007. Data Analysis Using Regression and Hierarchical/Multilevel Models. New York: Cambridge University Press.",
    "González, Susana G. 2014. “Aumenta en México la población indígena: Cepal.” La Jornada, July 6.",
    "González Navarro, Moisés. 1968. “El mestizaje Mexicano en el periodo nacional.” Revista Mexicana de Sociología 30 (1): 35–52.",
    "Guillaumin, Colette. 1995. Racism, Sexism, Power, and Ideology. London: Routledge.",
    "Gutiérrez Chong, Natividad. 2012. Mitos nacionalistas e identidades étnicas: Los intelectuales indígenas y el Estado Mexicano. Mexico City: UNAM—Instituto de Investigaciones Sociales.",
    "Hale, Charles A. 1968. Mexican Liberalism in the Age of Mora, 1821–1853. New Haven, Conn.: Yale University Press.",
    "Hale, Charles R. 2002. “Does Multiculturalism Menace? Governance, Cultural Rights and the Politics of Identity in Guatemala.” Journal of Latin American Studies 34 (3): 485–524.",
    "Harris, David R., and Jeremiah Joseph Sim. 2002. “Who Is Multiracial? Assessing the Complexity of Lived Race.” American Sociological Review 67 (4): 614–27.",
    "Hirschman, Charles. 1993. “How to Measure Ethnicity: An Immodest Proposal.” Pp. 547–60 in Challenges of Measuring an Ethnic World: Science, Politics, and Reality. Washington, D.C.: Government Printing Ofﬁce.",
    "Hochschild, Jennifer L., and Brenna M. Powell. 2008. “Racial Reorganization and the United States Census, 1850–1930: Mulattoes, Half-Breeds, Mixed Parentage, Hindoos, and the Mexican Race.” Studies in American Political Development 22 (1): 59–96.",
    "Hooker, Juliet. 2005. “Indigenous Inclusion/Black Exclusion: Race, Ethnicity and Multicultural Citizenship in Latin America.” Journal of Latin American Studies 37 (2): 285–310.",
    "Horowitz, Donald L. 1985. Ethnic Groups in Conﬂict. Berkeley: University of California Press.",
    "Hout, Michael, and Joshua R. Goldstein. 1994. “How 4.5 Million Irish Immigrants Became 40 Million Irish Americans: Demographic and Subjective Aspects of the Ethnic Composition of White Americans.” American Sociological Review 59 (1): 64–82.",
    "American Journal of Sociology 158",
    "INEGI (Instituto Nacional de Estadística y Geografía). 2011. “Marco Conceptual del",
    "Censo General de Población y Vivienda 2010.” INEGI, Mexico City.",
    "INEGI (Instituto Nacional de Estadística y Geografía). 2020. “Marco Conceptual del",
    "Censo General de Población y Vivienda 2020.” INEGI, Mexico City.",
    "Jung, Courtney. 2003. “The Politics of Indigenous Identity: Neoliberalism, Cultural Rights, and the Mexican Zapatistas.” Social Research: An International Quarterly",
    "70 (2): 433–61.",
    "Kertzer, David I., and Dominique Arel, eds. 2002. Census and Identity: The Politics of Race, Ethnicity, and Language in National Censuses, vol. 1. Cambridge: Cambridge",
    "University Press.",
    "Knight, Alan. 1990. “Racism, Revolution, and Indigenismo: Mexico, 1910–1940.” Pp. 71–",
    "113 in The Idea of Race in Latin America, 1870–1940, edited by Richard Graham. Austin: University of Texas Press.",
    "Lamont, Michèle, and Virág Molnár. 2002. “The Study of Boundaries in the Social Sciences.” Annual Review of Sociology 28:167–95.",
    "Lomnitz-Adler, Claudio. 1992. Exits from the Labyrinth: Culture and Ideology in the Mexican National Space. Berkeley and Los Angeles: University of California Press.",
    "Loveman, Mara. 1999. “Is ‘Race’ Essential?” American Sociological Review 64 (6): 891–98.",
    "Loveman, Mara. 2007. “The US Census and the Contested Rules of Racial Classiﬁcation in Early Twentieth-Century Puerto Rico.” Caribbean Studies 35 (2): 79–114.",
    "Loveman, Mara. 2014. National Colors: Racial Classiﬁcation and the State in Latin America. New York: Oxford University Press.",
    "Loveman, Mara, and Jeronimo O. Muniz. 2007. “How Puerto Rico Became White: Boundary Dynamics and Intercensus Racial Reclassiﬁcation.” American Sociological",
    "Review 72 (6): 915–39.",
    "Martínez Casas, Regina. 2007. Vivir Invisibles: La resigniﬁcación de los otomíes urbanos en Guadalajara. Mexico City: CIESAS.",
    "Martínez Casas, Regina. 2010. Profesionalización de Jóvenes Indígenas: El caso del IFP en México. Mexico City: CIESAS.",
    "Martínez Casas, Regina, Emiko Saldívar, René D. Flores, and Christina A. Sue. 2014. “The Different Faces of Mestizaje: Ethnicity and Race in Mexico.” Pp. 36–80 in",
    "Pigmentocracies: Ethnicity, Race, and Color in Latin America, edited by Edward Telles and PERLA. Chapel Hill: University of North Carolina Press.",
    "Martínez Novo, Carmen. 2006. Who Deﬁnes Indigenous? Identities, Development, Intellectuals and the State in Northern Mexico. New Brunswick, N.J.: Rutgers University Press.",
    "Monk, Ellis P., Jr. 2016. “The Consequences of ‘Race and Color’ in Brazil.” Social Problems 63 (3): 413–30.",
    "Mora, G. Cristina. 2014. “Cross-Field Effects and Ethnic Classiﬁcation: The Institutionalization of Hispanic Panethnicity, 1965 to 1990.” American Sociological Review 79 (2): 183–210.",
    "Muñoz, Carlos. 2007. Youth, Identity, Power: The Chicano Movement. London: Verso.",
    "Nagel, Joane. 1994. “Constructing Ethnicity: Creating and Recreating Ethnic Identity and Culture.” Social Problems 41 (1): 152–76.",
    "Nagel, Joane. 1995. “American Indian Ethnic Renewal: Politics and the Resurgence of Identity.” American Sociological Review 60 (6): 947–65.",
    "Olivé, León. 1999. Heurística, multiculturalismo y consenso. Mexico City: Universidad Nacional Autónoma de Mexico.",
    "Omi, Michael, and Howard Winant. 2014. Racial Formation in the United States. New York: Routledge.",
    "Preston, Samuel H., Patrick Heuveline, and Michel Guillot. 2001. Demography: Measuring and Modeling Population Processes. Malden, Mass.: Blackwell. Pryor, Edward T., Gustave J. Goldmann, Michael J. Sheridan, and Pamela M. White.",
    "1992. “Measuring Ethnicity: Is ‘Canadian’ an Evolving Indigenous Category?” Ethnic and Racial Studies 15 (2): 214–35. Boundary Crossing",
    "159",
    "Rasinski, Kenneth A. 1989. “The Effect of Question Wording on Public Support for Government Spending.” Public Opinion Quarterly 53 (3): 388–94.",
    "Reina, Leticia. 2011. Indio, campesino y nación: Historia e historiografía de los movimientos rurales. Mexico City: Siglo XXI.",
    "Saldívar, Emiko. 2008. Prácticas cotidianas del estado:Unaetnografía del ndigenismo Mexico. Mexico City: Universidad Iberoamericana.",
    "Schuman, Howard, and Stanley Presser. 1996. Questions and Answers in Attitude Surveys: Experiments on Question Form, Wording, and Context. Thousand Oaks, Calif.: Sage.",
    "Sewell, William H. 2004. “The Concept(s) of Culture.” Pp. 76–95 in Practicing History. New York: Routledge.",
    "Spillman, Lyn. 2020. What Is Cultural Sociology? Hoboken, N.J.: Wiley.",
    "Stavenhagen, Rodolfo. 2001. La Cuestión Étnica. Mexico City: COLMEX.",
    "Sue, Christina A. 2013. Land of the Cosmic Race: Race Mixture, Racism, and Blackness in Mexico. Oxford: Oxford University Press.",
    "Sue, Christina A., and Fernando Riosmena. 2021. “Black and Indigenous Inequality in Mexico: Implications for Multiracialism and Intersectionality Research.” Sociology of Race and Ethnicity 7 (4): 488–511.",
    "Sulmont, David. 2010. “Raza y etnicidad desde las encuestas sociales y de opinión: Dime cuántos quieres encontrar y te diré qué preguntar.” Unpublished manuscript. Pontiﬁcia Universidad Católica del Perú.",
    "Swidler, Ann. 1986. “Culture in Action: Symbols and Strategies.” American Sociological Review 51 (2): 273–86.",
    "Telles, Edward, and René Flores. 2013. “Not Just Color: Whiteness, Nation, and Status in Latin America.” Hispanic American Historical Review 93 (3): 411–49.",
    "Telles, Edward, René D. Flores, and Fernando Urrea-Giraldo. 2015. “Pigmentocracies: Educational Inequality, Skin Color and Census Ethnoracial Identiﬁcation in Eight",
    "Latin American Countries.” Research in Social Stratiﬁcation and Mobility 40:39–58.",
    "Telles, Edward, and Tianna Paschel. 2014. “Who Is Black, White, or Mixed Race? How Skin Color, Status, and Nation Shape Racial Classiﬁcation in Latin America.” American Journal of Sociology 120 (3): 864–907.",
    "Telles, Edward, and Christina A. Sue. 2019. Durable Ethnicity: Mexican Americans and the Ethnic Core. Oxford: Oxford University Press.",
    "Telles, Edward, and Florencia Torche. 2019. “Varieties of Indigeneity in the Americas.”",
    "Social Forces 97 (4): 1543–70.",
    "Telles, Edward E. 2002. “Racial Ambiguity among the Brazilian Population.” Ethnic and Racial Studies 25 (3): 415–41.",
    "Telles, Edward E., and Nelson Lim. 1998. “Does It Matter Who Answers the Race Question? Racial Classiﬁcation and Income Inequality in Brazil.” Demography 35 (4): 465–74.",
    "Telles, Edward E., and PERLA (Project on Race and Ethnicity in Latin America). 2014. Pigmentocracies: Ethnicity, Race, and Color in Latin America. Chapel Hill: University of North Carolina Press.",
    "Vasconcelos, José. (1925) 1992. La raza Cósmica. Mexico City: Espasa Calpe.",
    "Vázquez Sandrin, Germán, and María Félix Quezada. 2015. “Los indígenas autoadscritos de México en el censo 2010: Revitalización étnica o sobreestimación censal?” Papeles de Población 21 (86): 171–218.",
    "Villarreal, Andrés. 2014. “Ethnic Identiﬁcation and Its Consequences for Measuring Inequality in Mexico.” American Sociological Review 79 (4): 775–806.",
    "Waters, Mary C. “Ethnic and Racial Identities of Second-Generation Black Immigrants in New York City.” International migration Review 28, no. 4 (1994): 795–820.",
    "Wimmer, Andreas. 2008. “The Making and Unmaking of Ethnic Boundaries: A Multilevel Process Theory.” American Journal of Sociology 113 (4): 970–1022.",
    "Yashar, Deborah J. 2005. Contesting Citizenship in Latin America: The Rise of Indigenous Movements and the Postliberal Challenge. Cambridge: Cambridge University Press.",
    "American Journal of Sociology 160",
    "Zavala, Silvio, José Miranda, and Alfonso Caso. 1954. Métodos y Resultados de la Política Indigenista en México. Memorias del Instituto Nacional Indigenista 6. Mexico City:",
    "Ediciones del Instituto Nacional Indigenista.",
    "Zolberg, Aristide R., and Long Litt Woon. 1999. “Why Islam Is Like Spanish: Cultural Incorporation in Europe and the United States.” Politics and Society 27 (1): 5–38.",
    "Boundary Crossing 161",
]


def filter_data_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add a UI on top of dataframe to let viewers filter columns
    """
    # Add a checkbox to let user decide if he wants to filter the dataframe
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    modification_container = st.container()
    with modification_container:
        filterable_columns = ["publication_year", "journal_name", "language"]
        to_filter_columns = st.multiselect("Filter dataframe on", filterable_columns)

        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]

            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]

            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


def process_pdf():
    """Take uploaded PDF from the user and store extracted data in session."""
    pdf_file = st.file_uploader("Choose your .pdf file", type="pdf")
    extract_references = st.checkbox(
        "Extract references",
        value=True,
        key=None,
        help="Disable for debugging purposes and faster results "
        "if you only want to check the PDF parsing of "
        "title, authors and abstract.",
    )

    if pdf_file:
        with st.spinner(text="Processing PDF"):
            response = requests.post(
                url=BACKEND_URL + "/pdf",
                files={"pdf_file": pdf_file.getvalue()},
                params={"extract_references": extract_references},
            )

        show_pdf_data(response.json())


def show_pdf_data(pdf_data: dict) -> None:
    st.markdown("#### Your PDF")

    st.text_input(
        "Title",
        value=pdf_data.get("title"),
        key="pdf_title",
        help="The title we extracted from your PDF",
    )
    st.text_input(
        "Authors",
        value=", ".join(pdf_data.get("authors")),
        key="pdf_authors",
        help="The authors we extracted from your PDF",
    )
    st.text_area(
        "Abstract",
        value=pdf_data.get("abstract"),
        key="pdf_abstract",
        help="The abstract we extracted from your PDF",
    )

    _references = pdf_data.get("references")
    _references = st.session_state.references
    _references = pd.Series(_references, name="References")
    references = st.data_editor(_references, use_container_width=True)

    st.session_state.references = list(references)

    show_model_selection()


def show_model_selection():
    options = [
        "(All)",
        "bertopic",
        "cosine",
        "fuzzymatch",
        "spacy",
        "tfidf_all",
    ]
    st.session_state.model = st.selectbox(
        "What model would should be used to select the reviewers?", options
    )

    st.button(
        "Continue",
        key=None,
        help="Match references in PDF with OpenAlex works.",
        on_click=match_references,
        args=[st.session_state.references],
        use_container_width=False,
    )


def match_references(references: list[str]) -> None:
    with st.spinner(text="Matching references from PDF with OpenAlex works..."):
        response = requests.post(BACKEND_URL + "/openalex_references", json=references)
        st.session_state.openalex_works = response.json()

    st.write("Matched references.")
    st.write("Continuing with generating candidate works...")
    candidate_works(st.session_state.openalex_works)


def candidate_works(openalex_works: list[str]):
    with st.spinner(text="Generating candidates..."):
        response = requests.post(BACKEND_URL + "/candidate_works", json=openalex_works)
        st.session_state.candidate_works = response.json()

    st.write("Generated candidate works.")
    st.write("Continuing with selecting reviewers / works...")

    results()


def results():
    with st.spinner(text="Generating results..."):
        response = requests.post(
            BACKEND_URL + "/reviewers",
            json={
                "candidate_works": candidate_works,
                "model": st.session_state.model,
            },
        )
        st.session_state.results = response.json()
        st.dataframe(st.session_state.results)


process_pdf()

st.divider()
debug_expander = st.expander("Debug information:")
debug_expander.write("references")
debug_expander.write(references)
debug_expander.write("st.session_state")
debug_expander.write(st.session_state)
