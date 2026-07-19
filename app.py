import streamlit as st
import pandas as pd
import os

# =========================
# CONFIGURATION
# =========================

st.set_page_config(
    page_title="SMQ Dashboard",
    page_icon="📊",
    layout="wide"
)

FILE = "database_smq.xlsx"

# وظيفة مساعدة لحفظ البيانات في الشيت المناسبة دون مسح الشيتات الأخرى
def save_to_excel(df_to_save, sheet_name):
    with pd.ExcelWriter(
        FILE,
        engine="openpyxl",
        mode="a",
        if_sheet_exists="replace"
    ) as writer:
        df_to_save.to_excel(writer, sheet_name=sheet_name, index=False)

# =========================
# SESSION
# =========================

if "connected" not in st.session_state:
    st.session_state.connected = False

# =========================
# PAGE LOGIN
# =========================

if not st.session_state.connected:
    st.markdown(
        """
        <style>
        .stApp{
            background:linear-gradient(
                135deg,
                #ffb347,
                #ff8c42,
                #0f4c81
            );
        }
        [data-testid="stForm"]{
            background:white;
            padding:40px;
            border-radius:25px;
            box-shadow:0px 8px 25px rgba(0,0,0,0.3);
        }
        label{
            color:black !important;
            font-weight:bold;
        }
        input{
            color:black !important;
            background:white !important;
        }
        h1{
            color:white !important;
            text-align:center;
        }
        button{
            background:#0f4c81 !important;
            color:white !important;
            font-weight:bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # LOGO
    if os.path.exists("logo.png"):
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            st.image("logo.png", width=220)

    st.title("📊 SMQ Dashboard")
    st.write("Système de Management de la Qualité")

    with st.form("login_form"):
        username = st.text_input("👤 Identifiant")
        password = st.text_input("🔑 Mot de passe", type="password")
        login = st.form_submit_button("🚀 Connexion")

        if login:
            if username == "admin" and password == "qualite2026":
                st.session_state.connected = True
                st.rerun()
            else:
                st.error("Identifiant ou mot de passe incorrect ❌")

# =========================
# APPLICATION
# =========================
else:
    # SIDEBAR
    st.sidebar.title("🏢 SMQ")

    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", width=120)

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Accueil",
            "⚠️ Non-Conformités",
            "🔍 Audits",
            "📢 Réclamations",
            "🛠️ Actions Correctives",
            "📈 Statistiques"
        ]
    )

    if st.sidebar.button("🚪 Déconnexion"):
        st.session_state.connected = False
        st.rerun()

    # =========================
    # ACCUEIL
    # =========================
    if page == "🏠 Accueil":
        st.title("📊 Tableau de Bord SMQ")
        try:
            nc = pd.read_excel(FILE, sheet_name="NonConformites")
            audits = pd.read_excel(FILE, sheet_name="Audits")
            reclamations = pd.read_excel(FILE, sheet_name="Reclamations")
            actions = pd.read_excel(FILE, sheet_name="Actions")

            total = len(nc)
            ouvertes = len(nc[nc["Statut"] == "Ouverte"]) if "Statut" in nc.columns else 0
            fermees = len(nc[nc["Statut"] == "Fermée"]) if "Statut" in nc.columns else 0
            taux = round((fermees / total) * 100, 2) if total > 0 else 0

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("📌 Total NC", total)
            c2.metric("⚠️ Ouvertes", ouvertes)
            c3.metric("✅ Fermées", fermees)
            c4.metric("📊 Conformité", f"{taux}%")
            c5.metric("🔍 Audits", len(audits))

            st.divider()
            st.subheader("📋 Dernières Non-Conformités")
            st.dataframe(nc.tail(10), use_container_width=True)

        except Exception as e:
            st.error(f"Erreur Excel : {e}")

    # =========================
    # NON-CONFORMITES
    # =========================
    elif page == "⚠️ Non-Conformités":
        st.title("⚠️ Gestion des Non-Conformités")
        try:
            df = pd.read_excel(FILE, sheet_name="NonConformites")

            st.subheader("🔎 Recherche et filtres")
            recherche = st.text_input("Rechercher")
            col1, col2, col3 = st.columns(3)
            
            service = col1.selectbox("Service", ["Tous"] + list(df["Service"].unique()) if "Service" in df.columns else ["Tous"])
            statut = col2.selectbox("Statut", ["Tous"] + list(df["Statut"].unique()) if "Statut" in df.columns else ["Tous"])
            priorite = col3.selectbox("Priorité", ["Tous"] + list(df["Priorite"].unique()) if "Priorite" in df.columns else ["Tous"])

            resultat = df.copy()
            if recherche:
                resultat = resultat[resultat.astype(str).apply(lambda x: x.str.contains(recherche, case=False)).any(axis=1)]
            if service != "Tous" and "Service" in df.columns:
                resultat = resultat[resultat["Service"] == service]
            if statut != "Tous" and "Statut" in df.columns:
                resultat = resultat[resultat["Statut"] == statut]
            if priorite != "Tous" and "Priorite" in df.columns:
                resultat = resultat[resultat["Priorite"] == priorite]

            st.dataframe(resultat, use_container_width=True)
            st.divider()

            # AJOUTER
            st.subheader("➕ Ajouter une Non-Conformité")
            with st.form("ajout_nc"):
                date = st.date_input("Date")
                service_new = st.text_input("Service")
                description = st.text_area("Description")
                cause = st.text_input("Cause")
                statut_new = st.selectbox("Statut", ["Ouverte", "Fermée"])
                priorite_new = st.selectbox("Priorité", ["Haute", "Moyenne", "Basse"])
                ajouter = st.form_submit_button("➕ Ajouter")

                if ajouter:
                    nouvelle_ligne = pd.DataFrame([{
                        "ID": len(df) + 1, "Date": str(date), "Service": service_new,
                        "Description": description, "Cause": cause, "Statut": statut_new, "Priorite": priorite_new
                    }])
                    nouveau = pd.concat([df, nouvelle_ligne], ignore_index=True)
                    save_to_excel(nouveau, "NonConformites")
                    st.success("Ajout effectué ✅")
                    st.rerun()

            if not df.empty and "ID" in df.columns:
                st.divider()
                # MODIFICATION & SUPPRESSION
                st.subheader("✏️ Modifier / 🗑️ Supprimer une Non-Conformité")
                id_modif = st.selectbox("Choisir ID", df["ID"])
                ligne = df[df["ID"] == id_modif].iloc[0]

                with st.form("modification_nc"):
                    service_m = st.text_input("Service", ligne["Service"] if "Service" in df.columns else "")
                    desc_m = st.text_area("Description", ligne["Description"] if "Description" in df.columns else "")
                    cause_m = st.text_input("Cause", ligne["Cause"] if "Cause" in df.columns else "")
                    statut_m = st.selectbox("Statut", ["Ouverte", "Fermée"], index=0 if ("Statut" in df.columns and ligne["Statut"] == "Ouverte") else 1)
                    priorite_m = st.selectbox("Priorité", ["Haute", "Moyenne", "Basse"], index=["Haute", "Moyenne", "Basse"].index(ligne["Priorite"]) if "Priorite" in df.columns else 0)
                    modifier = st.form_submit_button("💾 Enregistrer les modifications")

                    if modifier:
                        index = df[df["ID"] == id_modif].index
                        df.loc[index, "Service"] = service_m
                        df.loc[index, "Description"] = desc_m
                        df.loc[index, "Cause"] = cause_m
                        df.loc[index, "Statut"] = statut_m
                        df.loc[index, "Priorite"] = priorite_m
                        save_to_excel(df, "NonConformites")
                        st.success("Modification enregistrée ✅")
                        st.rerun()

                if st.button("🗑️ Supprimer cette Non-Conformité"):
                    df = df[df["ID"] != id_modif]
                    save_to_excel(df, "NonConformites")
                    st.success("Suppression effectuée ✅")
                    st.rerun()
        except Exception as e:
            st.error(e)

    # =========================
    # AUDITS
    # =========================
    elif page == "🔍 Audits":
        st.title("🔍 Gestion des Audits")
        try:
            df = pd.read_excel(FILE, sheet_name="Audits")
            st.dataframe(df, use_container_width=True)

            st.subheader("📊 Résultat des audits")
            if "Résultat" in df.columns:
                st.bar_chart(df["Résultat"].value_counts())

            st.divider()
            st.subheader("➕ Ajouter un Audit")
            with st.form("ajout_audit"):
                date_a = st.date_input("Date Audit")
                type_a = st.text_input("Type / Champ de l'audit")
                auditeur = st.text_input("Auditeur")
                resultat_a = st.selectbox("Résultat", ["Conforme", "A améliorer", "Non-Conforme"])
                ajouter_a = st.form_submit_button("➕ Ajouter Audit")

                if ajouter_a:
                    nouvelle_ligne = pd.DataFrame([{"ID": len(df) + 1, "Date": str(date_a), "Type": type_a, "Auditeur": auditeur, "Résultat": resultat_a}])
                    nouveau = pd.concat([df, nouvelle_ligne], ignore_index=True)
                    save_to_excel(nouveau, "Audits")
                    st.success("Audit ajouté ✅")
                    st.rerun()

            if not df.empty and "ID" in df.columns:
                st.subheader("🗑️ Supprimer un Audit")
                id_supp_a = st.selectbox("Choisir ID Audit à supprimer", df["ID"])
                if st.button("🗑️ Supprimer l'audit"):
                    df = df[df["ID"] != id_supp_a]
                    save_to_excel(df, "Audits")
                    st.success("Audit supprimé ✅")
                    st.rerun()
        except Exception as e:
            st.error(e)

    # =========================
    # RECLAMATIONS
    # =========================
    elif page == "📢 Réclamations":
        st.title("📢 Réclamations Clients")
        try:
            df = pd.read_excel(FILE, sheet_name="Reclamations")
            st.dataframe(df, use_container_width=True)

            st.subheader("📊 Etat des réclamations")
            if "Statut" in df.columns:
                st.bar_chart(df["Statut"].value_counts())

            st.divider()
            st.subheader("➕ Ajouter une Réclamation")
            with st.form("ajout_rec"):
                date_r = st.date_input("Date Réclamation")
                client = st.text_input("Client")
                sujet = st.text_area("Sujet / Description")
                statut_r = st.selectbox("Statut", ["En cours", "Traitée", "Clôturée"])
                ajouter_r = st.form_submit_button("➕ Ajouter Réclamation")

                if ajouter_r:
                    nouvelle_ligne = pd.DataFrame([{"ID": len(df) + 1, "Date": str(date_r), "Client": client, "Description": sujet, "Statut": statut_r}])
                    nouveau = pd.concat([df, nouvelle_ligne], ignore_index=True)
                    save_to_excel(nouveau, "Reclamations")
                    st.success("Réclamation ajoutée ✅")
                    st.rerun()

            if not df.empty and "ID" in df.columns:
                st.subheader("🗑️ Supprimer une Réclamation")
                id_supp_r = st.selectbox("Choisir ID Réclamation à supprimer", df["ID"])
                if st.button("🗑️ Supprimer la réclamation"):
                    df = df[df["ID"] != id_supp_r]
                    save_to_excel(df, "Reclamations")
                    st.success("Réclamation supprimée ✅")
                    st.rerun()
        except Exception as e:
            st.error(e)

    # =========================
    # ACTIONS CORRECTIVES
    # =========================
    elif page == "🛠️ Actions Correctives":
        st.title("🛠️ Suivi des Actions Correctives")
        try:
            df = pd.read_excel(FILE, sheet_name="Actions")
            st.dataframe(df, use_container_width=True)

            st.subheader("📈 Avancement des actions")
            if "Avancement" in df.columns:
                st.bar_chart(df["Avancement"].value_counts())

            st.divider()
            st.subheader("➕ Ajouter une Action Corrective")
            with st.form("ajout_action"):
                action_desc = st.text_area("Description de l'action")
                resp = st.text_input("Responsable")
                delai = st.date_input("Délai")
                avancement = st.selectbox("Avancement", ["Non commencée", "En cours", "Terminée"])
                ajouter_act = st.form_submit_button("➕ Ajouter Action")

                if ajouter_act:
                    nouvelle_ligne = pd.DataFrame([{"ID": len(df) + 1, "Action": action_desc, "Responsable": resp, "Délai": str(delai), "Avancement": avancement}])
                    nouveau = pd.concat([df, nouvelle_ligne], ignore_index=True)
                    save_to_excel(nouveau, "Actions")
                    st.success("Action ajoutée ✅")
                    st.rerun()

            if not df.empty and "ID" in df.columns:
                st.subheader("🗑️ Supprimer une Action")
                id_supp_act = st.selectbox("Choisir ID Action à supprimer", df["ID"])
                if st.button("🗑️ Supprimer l'action"):
                    df = df[df["ID"] != id_supp_act]
                    save_to_excel(df, "Actions")
                    st.success("Action supprimée ✅")
                    st.rerun()
        except Exception as e:
            st.error(e)

    # =========================
    # STATISTIQUES
    # =========================
    elif page == "📈 Statistiques":
        st.title("📈 Statistiques Qualité Globale")
        try:
            nc = pd.read_excel(FILE, sheet_name="NonConformites")
            audits = pd.read_excel(FILE, sheet_name="Audits")
            reclamations = pd.read_excel(FILE, sheet_name="Reclamations")

            c1, c2, c3 = st.columns(3)
            c1.metric("⚠️ Non-Conformités", len(nc))
            c2.metric("🔍 Audits", len(audits))
            c3.metric("📢 Réclamations", len(reclamations))

            st.divider()

            if "Service" in nc.columns:
                st.subheader("📊 NC par Service")
                st.bar_chart(nc["Service"].value_counts())

            if "Statut" in nc.columns:
                st.subheader("📊 NC par Statut")
                st.bar_chart(nc["Statut"].value_counts())

            if "Priorite" in nc.columns:
                st.subheader("🚨 NC par Priorité")
                st.bar_chart(nc["Priorite"].value_counts())
        except Exception as e:
            st.error(e)