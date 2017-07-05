__author__ = 'Ronald'


from ...modules import *

prefix_cron = Blueprint('cron', __name__)


@prefix_cron.route('/tache')
def tache():

    from ..tache.models_tache import Tache

    all_tache = Tache.objects(updated__notified=True)

    time_zones = pytz.timezone('Africa/Douala')
    date_now = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    titre = 'Notification de votre tache'

    for taches in all_tache:
        for item in taches.notified():

            # dif = date_now - item.date

            dif = datetime.datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(item.date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")

            if dif.seconds >= 3600:
                create = 0
                date = str(function.format_date(item.date, '%d/%m/%Y'))
                user = item.user.first_name+" "+item.user.last_name

                msg = Message()
                msg.subject = 'Notification FDT'
                msg.sender = ("Application FDT", "no_reply@accentcom.agency")

                subtitle = 'Creation de la tache'
                if item.action == 'creation':
                    create = 1
                    msg.recipients = [taches.user_id.email]

                else:
                    msg.recipients = [taches.user_id.email]
                    if item.action == 'open_end':
                        create = 2
                        subtitle = 'Fin d\'execution de la tache'
                        if taches.projet_id:
                            msg.recipients = [taches.projet_id.responsable_id.email]
                    elif item.action == 'end_close':
                        create = 3
                        subtitle = 'Cloture de la tache'

                    elif item.action == 'formation':
                        create = 4
                        subtitle = 'Creation d\'une tache de formation'
                    else:
                        subtitle = 'Modification de la tache'

                msg.html = render_template('mail/tache_mail.html', titre=titre, subtitle=subtitle, tache=taches, create=create, date=date, user=user)
                mail.send(msg)
    all_tache.update(set__updated__S__notified=False)

    return 'ok'


@prefix_cron.route('/projet')
def projet():

    from ..tache.models_tache import Tache, Projet
    from ..user.models_user import UserRole

    all_projet = Projet.objects(updated__notified=True)

    time_zones = pytz.timezone('Africa/Douala')
    date_now = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    titre = 'Notification de votre tache'

    for projets in all_projet:
        for item in projets.notified():
            # dif = date_now - item.date
            dif = datetime.datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(item.date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            if dif.seconds >= 3600:
                create = 0
                date = str(function.format_date(item.date), '%d/%m/%Y')
                user = item.user.first_name+" "+item.user.last_name

                subtitle = ' Creation du projet'

                utilisateur = False
                if item.action == 'creation':
                    create = 1
                    recipients = [projets.responsable_id.email]

                else:

                    recipients = [projets.responsable_id.email]
                    if item.action == 'creation_demande':
                        create = 2
                        subtitle = ' Creation d\'une demande de projet'
                        recipients = None

                    elif item.action == 'modification_demande':
                        create = 3
                        subtitle = ' Modification de la demande de projet'
                        recipients = None

                    elif item.action == 'relance_demande':
                        create = 4
                        subtitle = 'Relance d\'une demande de projet'
                        recipients = None

                    elif item.action == 'valide_demande':
                        create = 5
                        subtitle = 'Validation du projet'

                    elif item.action == 'attente_rejet_demande':
                        create = 6
                        subtitle = 'Rejet du projet'

                    elif item.action == 'rejet_attente_demande':
                        create = 7
                        subtitle = 'Relance de demande de projet'
                        recipients = None

                    elif item.action == 'open_suspend':
                        create = 8
                        subtitle = 'Suspension du projet'
                        utilisateur = True

                    elif item.action == 'open_suspend':
                        create = 9
                        subtitle = 'Cloture du projet'
                        utilisateur = True

                    else:
                        subtitle = ' Modification du projet'

                if recipients:
                    msg = Message()
                    msg.recipients = recipients
                    msg.subject = 'Notification FDT'
                    msg.sender = ("Application FDT", "no_reply@accentcom.agency")
                    msg.html = render_template('mail/projet_mail.html', titre=titre, subtitle=subtitle, projet=projets, create=create, date=date, user=user)
                    mail.send(msg)
                else:
                    if not utilisateur:
                        user_role = UserRole.objects()
                        for users in user_role:
                            if users.role_id.valeur == 'projet_demande':
                                msg = Message()
                                msg.recipients = [users.user_id.email]
                                msg.subject = 'Notification FDT'
                                msg.sender = ("Application FDT", "no_reply@accentcom.agency")

                                msg.html = render_template('mail/projet_mail.html', titre=titre, subtitle=subtitle, projet=projets, create=create, date=date, user=user)
                                mail.send(msg)
                    else:
                        all_tache = Tache.objects(projet_id=projets.id)
                        for taches in all_tache:
                            msg = Message()
                            msg.recipients = [taches.user_id.email]
                            msg.subject = 'Notification FDT'
                            msg.sender = ("Application FDT", "no_reply@accentcom.agency")

                            msg.html = render_template('mail/projet_mail.html', titre=titre, subtitle=subtitle, projet=projets, create=create, date=date, user=user)
                            mail.send(msg)

    #
    all_projet.update(set__updated__S__notified=False)

    return 'ok'


@prefix_cron.route('/besoin')
def besoin():

    from ..projet.models_projet import BesoinFinancier

    time_zones = pytz.timezone('Africa/Douala')
    date_now = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    titre = 'Notification de votre besoin'

    all_besoin = BesoinFinancier.objects(updated__notified=True)

    for besoin in all_besoin:
        for item in besoin.notified():
            dif = datetime.datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(item.date.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            # dif = date_now - item.date
            if dif.seconds >= 3600:

                if item.action == 'valide_besoin':
                    subtitle = 'Validation du besoin financier'
                    create = 1
                    msg = Message()
                    msg.recipients = [item.projet_id.responsable_id.email]
                    msg.subject = 'Notification FDT'
                    msg.sender = ("Application FDT", "no_reply@accentcom.agency")

                    msg.html = render_template('mail/besoin_mail.html', titre=titre, subtitle=subtitle, besoin=besoin, create=create)
                    mail.send(msg)

                if item.action == 'rejet_besoin':
                    subtitle = 'Rejet du besoin financier'
                    create = 2
                    msg = Message()
                    msg.recipients = [item.projet_id.responsable_id.email]
                    msg.subject = 'Notification FDT'
                    msg.sender = ("Application FDT", "no_reply@accentcom.agency")

                    msg.html = render_template('mail/besoin_mail.html', titre=titre, subtitle=subtitle, besoin=besoin, create=create)
                    mail.send(msg)

    all_besoin.update(set__updated__S__notified=False)

    return 'ok'