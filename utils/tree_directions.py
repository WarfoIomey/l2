from django.db import connection
from laboratory.settings import TIME_ZONE


def root_direction(napravleniye):
    """
    парам: napravleniye

    Вернуть корневой узел среди Направлений:
    id-направления, дата создания, id-услуг(и) относящейся к данному направлению, уровень поиска. 1(корень)
    в SQL:
    nn - directions_napravleniya
    ii - directions_issledovaniya
    """

    with connection.cursor() as cursor:
        cursor.execute("""WITH RECURSIVE r AS (
               SELECT nn.id, 
               to_char(nn.data_sozdaniya AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_create,
               to_char(nn.data_sozdaniya AT TIME ZONE %(tz)s, 'HH24:MI:SS') as time_create,
               nn.parent_id, 
               ii.napravleniye_id,
               ii.id, 1 AS level
               FROM directions_issledovaniya ii 
               LEFT JOIN directions_napravleniya nn 
               ON ii.napravleniye_id=nn.id
                   WHERE nn.id = %(num_direction)s
               
               UNION ALL
              
               SELECT n.id, 
                      to_char(n.data_sozdaniya AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_create,
                      to_char(n.data_sozdaniya AT TIME ZONE %(tz)s, 'HH24:MI:SS') as time_create,
                      n.parent_id,
                      i.napravleniye_id,
                      i.id, r.level + 1 AS level
               FROM directions_issledovaniya i 
               LEFT JOIN directions_napravleniya n 
               ON i.napravleniye_id=n.id
               JOIN r
               ON r.parent_id = i.id
            )
            
            SELECT * FROM r;""",
                       params={'num_direction': napravleniye, 'tz': TIME_ZONE})

        row = cursor.fetchall()
    return row


def tree_direction(iss):
    """
    парам: услуга

    Вернуть стуркутру Направлений:
    id-направления, дата создания, id-услуг(и) относящейся к данному направлению, уровень поиска. 1(корень)
    в SQL:
    nn - directions_napravleniya
    ii - directions_issledovaniya
    """

    with connection.cursor() as cursor:
        cursor.execute("""WITH RECURSIVE r AS (
            SELECT nn.id, 
            to_char(nn.data_sozdaniya AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_create,
            to_char(nn.data_sozdaniya AT TIME ZONE %(tz)s, 'HH24:MI') as time_create,
            nn.parent_id, 
            ii.napravleniye_id,
            ii.id as iss, 
            to_char(ii.time_confirmation AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_confirm, 
            to_char(ii.time_confirmation AT TIME ZONE %(tz)s, 'HH24:MI') as time_confirm, 
            ii.research_id, ddrr.title,
            ii.diagnos, 1 AS level
            FROM directions_issledovaniya ii 
            LEFT JOIN directions_napravleniya nn 
            ON ii.napravleniye_id=nn.id
            LEFT JOIN directory_researches ddrr
            ON ii.research_id = ddrr.id
            
            WHERE ii.id = %(num_issledovaniye)s
            
            UNION ALL
            
            SELECT n.id, 
                  to_char(n.data_sozdaniya AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_create,
                  to_char(n.data_sozdaniya AT TIME ZONE %(tz)s, 'HH24:MI') as time_create,
                  n.parent_id,
                  i.napravleniye_id,
                  i.id, 
                  to_char(i.time_confirmation AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_confirm, 
                  to_char(i.time_confirmation AT TIME ZONE %(tz)s, 'HH24:MI') as time_confirm,
                  i.research_id, dr.title,
                  i.diagnos, 
                  r.level + 1 AS level
            FROM directions_issledovaniya i 
            LEFT JOIN directions_napravleniya n 
            ON i.napravleniye_id=n.id
            LEFT JOIN directory_researches dr
            ON i.research_id = dr.id
            JOIN r
            ON r.iss = n.parent_id
            )
            
            SELECT * FROM r;""",
                       params={'num_issledovaniye': iss, 'tz': TIME_ZONE})

        row = cursor.fetchall()
    return row


def hospital_get_direction(iss, main_research, hosp_site_type, hosp_is_paraclinic, hosp_is_doc_refferal, hosp_is_lab):
    """
    парам: услуга
    Вернуть стуркутру в след порядке:
    num_dir, date_creat, time_create, parent_iss, num_dir,
    issled_id, date_confirm, time_confirm, id_research, title_research,
    diagnos, Level-подчинения, id_research,	id_podrazde, is_paraclinic,
    is_doc,	is_stom, is_hospital, is_micrbiology, title_podr,
    p_type_podr, site_type_hospital, slave_research_id
    в SQL:
    nn - directions_napravleniya
    ii - directions_issledovaniya
    """

    with connection.cursor() as cursor:
        cursor.execute("""WITH RECURSIVE r AS (
            SELECT nn.id, 
            to_char(nn.data_sozdaniya AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_create,
            to_char(nn.data_sozdaniya AT TIME ZONE %(tz)s, 'HH24:MI') as time_create,
            nn.parent_id, 
            ii.napravleniye_id,
            ii.id as iss, 
            to_char(ii.time_confirmation AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_confirm, 
            to_char(ii.time_confirmation AT TIME ZONE %(tz)s, 'HH24:MI') as time_confirm, 
            ii.research_id, ddrr.title,
            ii.diagnos, 1 AS level
            FROM directions_issledovaniya ii 
            LEFT JOIN directions_napravleniya nn 
            ON ii.napravleniye_id=nn.id
            LEFT JOIN directory_researches ddrr
            ON ii.research_id = ddrr.id
            WHERE ii.id = %(num_issledovaniye)s
            UNION ALL
            SELECT n.id, 
                  to_char(n.data_sozdaniya AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_create,
                  to_char(n.data_sozdaniya AT TIME ZONE %(tz)s, 'HH24:MI') as time_create,
                  n.parent_id,
                  i.napravleniye_id,
                  i.id, 
                  to_char(i.time_confirmation AT TIME ZONE %(tz)s, 'DD.MM.YYYY') as date_confirm, 
                  to_char(i.time_confirmation AT TIME ZONE %(tz)s, 'HH24:MI') as time_confirm,
                  i.research_id, dr.title,
                  i.diagnos, 
                  r.level + 1 AS level
            FROM directions_issledovaniya i 
            LEFT JOIN directions_napravleniya n 
            ON i.napravleniye_id=n.id
            LEFT JOIN directory_researches dr
            ON i.research_id = dr.id
            JOIN r
            ON r.iss = n.parent_id
            ),
            
            t_podrazdeleniye AS (SELECT podrazdeleniya_podrazdeleniya.id, title, p_type FROM podrazdeleniya_podrazdeleniya),
            
            t_research AS (SELECT directory_researches.id as research_id, podrazdeleniye_id, is_paraclinic, is_doc_refferal, 
            is_stom, is_hospital, is_microbiology, t_podrazdeleniye.title, t_podrazdeleniye.p_type FROM directory_researches
			    LEFT JOIN t_podrazdeleniye ON t_podrazdeleniye.id = directory_researches.podrazdeleniye_id),
			
			t_hospital_service AS (SELECT site_type, slave_research_id FROM directory_hospitalservice
            WHERE main_research_id = %(main_research)s)
            
            SELECT * FROM r
            LEFT JOIN t_research ON r.research_id = t_research.research_id
            LEFT JOIN t_hospital_service ON r.research_id = t_hospital_service.slave_research_id
            WHERE 
            CASE when %(hosp_site_type)s > -1 THEN 
            site_type = %(hosp_site_type)s
            when %(hosp_is_paraclinic)s = TRUE THEN
            is_paraclinic = true
            when %(hosp_is_doc_refferal)s = TRUE THEN
            is_doc_refferal = true and site_type is NULL
            when %(hosp_is_lab)s = TRUE THEN
            is_paraclinic = FALSE and is_doc_refferal = FALSE and is_stom = FALSE and is_hospital = FALSE and is_microbiology = FALSE        
            END 
            
			ORDER BY p_type, site_type, napravleniye_id;""",
        params={'num_issledovaniye': iss, 'main_research': main_research, 'hosp_site_type':hosp_site_type,
                'hosp_is_paraclinic':hosp_is_paraclinic, 'hosp_is_doc_refferal': hosp_is_doc_refferal,
                'hosp_is_lab': hosp_is_lab, 'tz': TIME_ZONE})
        row = cursor.fetchall()
    return row


def get_research_by_dir(numdir):
    """выход стр-ра:
    issledovaniya.id - для последующего поиска подчинений по исследованию
    directions_issledovaniya.research_id - является main_research
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT directions_issledovaniya.id, directions_issledovaniya.research_id 
            FROM directions_issledovaniya where napravleniye_id = %(num_dir)s
            """, params={'num_dir': numdir })

        row = cursor.fetchall()
    return row
