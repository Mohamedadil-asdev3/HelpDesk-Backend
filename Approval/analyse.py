# import MySQLdb
# from django.http import JsonResponse     # if using Django API

# db = MySQLdb.connect(
#     host="localhost",
#     user="root",
#     passwd="Stemz@123",
#     db="ticketing_system",
# )

# cursor = db.cursor()

# glpi_users_query = 'SELECT * FROM glpi_users;'   # No need for db name again


# def GlpiUsers(request):     # remove "self" if this is a Django function-based view
#     cursor.execute(glpi_users_query)
#     rows = cursor.fetchall()

#     # Convert result to list of dicts (optional but useful)
#     columns = [col[0] for col in cursor.description]
#     result = [dict(zip(columns, row)) for row in rows]

#     return result

# views.py
# Ticket/views.py
# Ticket/views.py

# Ticket/views.py
# Ticket/views.py

from django.http import JsonResponse
from django.views import View
import MySQLdb
from datetime import datetime, date
from collections import defaultdict

def get_db_connection():
    return MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="Stemz@123",
        db="old_approval_matrix",
        charset='utf8mb4',
        use_unicode=True
    )

# Priority mapping (GLPI standard: 1=Very Low, 2=Low, 3=Medium, 4=High, 5=Very High, 6=Major)
PRIORITY_MAP = {
    0: "All",
    1: "Very Low",
    2: "Low",
    3: "Medium",
    4: "High",
    5: "Very High",
    6: "Major"
}

# Status mapping for validation (from your original queries)
VALIDATION_STATUS_MAP = {
    2: "Pending",      # Pending approval
    3: "Approved",
    4: "Rejected",
    99: "On Hold",
    98: "SLA Breached", # Breached
    6: "Reassigned"    # If needed
}

class CeoApprovalDashboard(View):
    def get(self, request):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(MySQLdb.cursors.DictCursor)

            date1 = request.GET.get('date1', '2025-01-01')
            date2 = request.GET.get('date2', date.today().strftime('%Y-%m-%d'))
            today_str = date.today().strftime('%Y-%m-%d')
            month_start = date.today().replace(day=1).strftime('%Y-%m-%d')

            date_range = f"t.date BETWEEN '2025-01-01 00:00:00' AND '2025-11-24 23:59:59'"
            # date_range = f"t.date BETWEEN '{date1} 00:00:00' AND '{date2} 23:59:59'"

            today_filter = f"DATE(t.date) = '{today_str}'"
            month_filter = f"DATE(t.date) >= '{month_start}'"
            select_query =f"""
                SELECT
                    COUNT(DISTINCT t.id) AS total_tickets,
                    SUM(CASE WHEN DATE(t.date) = '{today_str}' THEN 1 ELSE 0 END) AS today_tickets,
                    SUM(CASE WHEN DATE(t.date) >= '{month_start}' THEN 1 ELSE 0 END) AS month_tickets,
                    SUM(CASE WHEN tv.status = 2 AND t.status != 6 THEN 1 ELSE 0 END) AS pending,
                    SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END) AS approved,
                    SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END) AS rejected,
                    SUM(CASE WHEN tv.status = 99 THEN 1 ELSE 0 END) AS on_hold,
                    SUM(CASE WHEN tv.status = 98 THEN 1 ELSE 0 END) AS sla_breached_count,
                    0 AS solved,  -- Adjust if you have solved logic
                    0 AS closed   -- Adjust if you have closed logic
                FROM glpi_tickets t
                LEFT JOIN glpi_ticketvalidations tv ON tv.tickets_id = t.id
                WHERE t.is_deleted = 0 AND {date_range}
            """
            # 1. Overall Counts (using your original summary query)
            cursor.execute(select_query)
            print("select_query1",select_query)
            overall_counts = cursor.fetchone()
            select_query =f"""
                SELECT 
                    t.id, t.name AS title, t.content AS description, t.date AS created_date, t.date_mod AS updated_date,
                    t.status, t.priority, t.users_id_recipient,
                    tv.status AS validation_status,
                    u.firstname, u.realname, u.name AS requester_name,
                    uc.name AS department
                FROM glpi_tickets t
                LEFT JOIN glpi_ticketvalidations tv ON tv.tickets_id = t.id
                LEFT JOIN glpi_users u ON t.users_id_recipient = u.id
                LEFT JOIN glpi_usercategories uc ON u.usercategories_id = uc.id
                WHERE t.is_deleted = 0 AND {date_range}
                ORDER BY t.date DESC
                LIMIT 500  -- Adjust based on your data size
            """
            print("select_query2",select_query)
            # 2. Fetch Detailed Tickets (limit to 100 per category for performance; paginate if needed)
            cursor.execute(select_query)
            tickets = cursor.fetchall()

            # 3. Process Overall + Ticket Lists
            overall = {
                "total_tickets": int(overall_counts['total_tickets'] or 0),
                "today_tickets": int(overall_counts['today_tickets'] or 0),
                "month_tickets": int(overall_counts['month_tickets'] or 0),
                "pending": int(overall_counts['pending'] or 0),
                "approved": int(overall_counts['approved'] or 0),
                "rejected": int(overall_counts['rejected'] or 0),
                "on_hold": int(overall_counts['on_hold'] or 0),
                "solved": int(overall_counts['solved'] or 0),
                "closed": int(overall_counts['closed'] or 0),
                "sla_breached_count": int(overall_counts['sla_breached_count'] or 0),
                "pending_tickets": [],
                "approved_tickets": [],
                "rejected_tickets": [],
                "on_hold_tickets": [],
                "solved_tickets": [],
                "closed_tickets": [],
                "sla_breached_tickets": []
            }

            # 4. Department & Priority Stats
            dept_stats = defaultdict(lambda: {
                "department": "", "total_tickets": 0, "pending": 0, "approved": 0, "rejected": 0,
                "on_hold": 0, "solved": 0, "closed": 0, "sla_breached_count": 0, "sla_breached_tickets": []
            })

            priority_stats = defaultdict(lambda: {
                "priority": "", "total_tickets": 0, "pending": 0, "approved": 0, "rejected": 0,
                "on_hold": 0, "solved": 0, "closed": 0, "sla_breached_count": 0, "sla_breached_tickets": []
            })

            for ticket in tickets:
                dept = ticket['department'] or "Unknown"
                prio_num = ticket['priority'] or 0
                prio_name = PRIORITY_MAP.get(prio_num, "Unknown")

                # Update stats
                dept_stats[dept]["department"] = dept
                dept_stats[dept]["total_tickets"] += 1
                priority_stats[prio_name]["priority"] = prio_name
                priority_stats[prio_name]["total_tickets"] += 1

                v_status = ticket['validation_status']
                status_name = VALIDATION_STATUS_MAP.get(v_status, "Unknown")

                # Format ticket
                formatted_ticket = self.format_ticket(ticket, status_name, dept, prio_name)

                # Categorize
                if v_status == 2 and ticket['status'] != 6:  # Pending
                    overall["pending_tickets"].append(formatted_ticket)
                    dept_stats[dept]["pending"] += 1
                    priority_stats[prio_name]["pending"] += 1
                elif v_status == 3:  # Approved
                    overall["approved_tickets"].append(formatted_ticket)
                    dept_stats[dept]["approved"] += 1
                    priority_stats[prio_name]["approved"] += 1
                elif v_status == 4:  # Rejected
                    overall["rejected_tickets"].append(formatted_ticket)
                    dept_stats[dept]["rejected"] += 1
                    priority_stats[prio_name]["rejected"] += 1
                elif v_status == 99:  # On Hold
                    overall["on_hold_tickets"].append(formatted_ticket)
                    dept_stats[dept]["on_hold"] += 1
                    priority_stats[prio_name]["on_hold"] += 1
                elif v_status == 98:  # SLA Breached
                    overall["sla_breached_tickets"].append(formatted_ticket)
                    dept_stats[dept]["sla_breached_count"] += 1
                    dept_stats[dept]["sla_breached_tickets"].append(formatted_ticket)
                    priority_stats[prio_name]["sla_breached_count"] += 1
                    priority_stats[prio_name]["sla_breached_tickets"].append(formatted_ticket)
                # Add elif for solved/closed based on t.status if needed (e.g., status 5=solved, 6=closed)

            # Convert to lists (limit ticket lists to avoid huge JSON)
            department_wise = list(dept_stats.values())[:20]  # Top 20 depts
            priority_wise = list(priority_stats.values())[:10]  # Top 10 priorities

            # Limit ticket arrays to 100 each for performance
            overall["pending_tickets"] = overall["pending_tickets"][:100]
            overall["approved_tickets"] = overall["approved_tickets"][:100]
            # ... similarly for others

            return JsonResponse({
                "success": True,
                "data": {
                    "overall": overall,
                    "department_wise": department_wise,
                    "priority_wise": priority_wise
                },
                "date_range": {"from": date1, "to": date2}
            })

        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e),
                "data": {}
            }, status=500)

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def format_ticket(self, ticket, status_name, dept, prio_name):
        return {
            "id": ticket['id'],
            "ticket_no": ticket['id'],  # Use GLPI ID as ticket_no
            "title": ticket['title'] or "No Title",
            "description": ticket['description'] or "",
            "created_date": ticket['created_date'].isoformat() if ticket['created_date'] else None,
            "updated_date": ticket['updated_date'].isoformat() if ticket['updated_date'] else None,
            "status_detail": {"field_values": status_name},
            "priority_detail": {"field_values": prio_name},
            "department_detail": {"field_name": dept},
            "requested_detail": {
                "name": f"{ticket['firstname'] or ''} {ticket['realname'] or ''}".strip() or ticket['requester_name'] or "Unknown",
                "email": ""  # Add glpi_users.email if needed
            },
            "location_detail": {"field_name": "Unknown"},  # Add glpi_locations if needed
            "category_detail": None,  # Add glpi_itilcategories if needed
            "subcategory_detail": None
        }
# Ticket/views.py
# from django.http import JsonResponse
# from django.views import View
# import MySQLdb
# from datetime import datetime

# def get_db_connection():
#     return MySQLdb.connect(
#         host="localhost",
#         user="root",
#         passwd="Stemz@123",
#         db="old_approval_matrix",
#         charset='utf8mb4',
#         use_unicode=True
#     )

# class CeoApprovalDashboard(View):
#     def get(self, request):
#         conn = None
#         cursor = None
#         try:
#             conn = get_db_connection()
#             cursor = conn.cursor(MySQLdb.cursors.DictCursor)

#             # Date range
#             date1 = request.GET.get('date1', '2025-01-01')
#             date2 = request.GET.get('date2', datetime.now().strftime('%Y-%m-%d'))
#             date_range = f"BETWEEN '{date1} 00:00:00' AND '{date2} 23:59:59'"

#             result = {}

#             # 1. Main Summary (Top Cards) - Fixed
#             cursor.execute(f"""
#                 SELECT
#                     COALESCE(SUM(CASE WHEN tv.status = 2 AND t.status != 6 THEN 1 ELSE 0 END), 0) AS pending,
#                     COALESCE(SUM(CASE WHEN tv.status = 99 THEN 1 ELSE 0 END), 0) AS hold,
#                     COALESCE(SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END), 0) AS approved,
#                     COALESCE(SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END), 0) AS rejected,
#                     COALESCE(SUM(CASE WHEN tv.status = 98 THEN 1 ELSE 0 END), 0) AS sla_breached
#                 FROM glpi_ticketvalidations tv
#                 INNER JOIN glpi_tickets t ON tv.tickets_id = t.id
#                 WHERE t.is_deleted = 0 
#                   AND t.date {date_range}
#             """)
#             summary = cursor.fetchone()
#             result['summary'] = {
#                 "pending": int(summary['pending']),
#                 "hold": int(summary['hold']),
#                 "approved": int(summary['approved']),
#                 "rejected": int(summary['rejected']),
#                 "sla_breached": int(summary['sla_breached'])
#             }

#             # 2. By Approver (HODs) - Fixed
#             cursor.execute(f"""
#                 SELECT
#                     CONCAT(u.firstname, ' ', u.realname) AS name,
#                     COALESCE(SUM(CASE WHEN tv.status = 2 AND t.status != 6 THEN 1 ELSE 0 END), 0) AS pending,
#                     COALESCE(SUM(CASE WHEN tv.status = 99 THEN 1 ELSE 0 END), 0) AS hold,
#                     COALESCE(SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END), 0) AS approved,
#                     COALESCE(SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END), 0) AS rejected,
#                     COALESCE(SUM(CASE WHEN tv.status = 98 THEN 1 ELSE 0 END), 0) AS sla_breached
#                 FROM glpi_ticketvalidations tv
#                 INNER JOIN glpi_tickets t ON tv.tickets_id = t.id
#                 INNER JOIN glpi_users u ON u.id = tv.users_id_validate
#                 WHERE t.is_deleted = 0 
#                   AND t.date {date_range}
#                   AND u.is_hod = 1
#                 GROUP BY u.id, u.firstname, u.realname
#                 ORDER BY u.firstname
#             """)
#             result['by_approver'] = cursor.fetchall()

#             # 3. Average Response Time - Fixed
#             cursor.execute("""
#                 SELECT
#                     CONCAT(u.firstname, ' ', u.realname) AS username,
#                     ROUND(COALESCE(AVG(TIMESTAMPDIFF(DAY, tv.submission_date, tv.validation_date)), 0), 1) AS avg_response_days
#                 FROM glpi_ticketvalidations tv
#                 INNER JOIN glpi_users u ON tv.users_id_validate = u.id
#                 WHERE tv.validation_date IS NOT NULL 
#                   AND u.is_hod = 1
#                 GROUP BY u.id, u.firstname, u.realname
#             """)
#             result['response_time'] = cursor.fetchall()

#             # 4. By Priority - Fixed
#             cursor.execute(f"""
#                 SELECT
#                     t.priority,
#                     COALESCE(SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END), 0) AS approved,
#                     COALESCE(SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END), 0) AS rejected,
#                     COALESCE(SUM(CASE WHEN tv.status = 99 THEN 1 ELSE 0 END), 0) AS on_hold,
#                     COALESCE(SUM(CASE WHEN tv.status = 98 THEN 1 ELSE 0 END), 0) AS sla_breached
#                 FROM glpi_tickets t
#                 LEFT JOIN glpi_ticketvalidations tv ON t.id = tv.tickets_id
#                 WHERE t.is_deleted = 0 
#                   AND t.date {date_range}
#                 GROUP BY t.priority
#                 ORDER BY t.priority
#             """)
#             result['by_priority'] = cursor.fetchall()

#             # 5. By Department - Fixed with ANY_VALUE
#             cursor.execute(f"""
#                 SELECT
#                     COALESCE(uc.name, 'Unknown') AS department,
#                     COALESCE(SUM(CASE WHEN tv.status = 2 THEN 1 ELSE 0 END), 0) AS pending,
#                     COALESCE(SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END), 0) AS approved,
#                     COALESCE(SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END), 0) AS rejected,
#                     COALESCE(SUM(CASE WHEN tv.status = 99 THEN 1 ELSE 0 END), 0) AS on_hold,
#                     COALESCE(SUM(CASE WHEN tv.status = 98 THEN 1 ELSE 0 END), 0) AS sla_breached
#                 FROM glpi_tickets t
#                 LEFT JOIN glpi_ticketvalidations tv ON t.id = tv.tickets_id
#                 LEFT JOIN glpi_users u ON u.id = t.users_id_recipient
#                 LEFT JOIN glpi_usercategories uc ON uc.id = u.usercategories_id
#                 WHERE t.is_deleted = 0 
#                   AND t.date {date_range}
#                 GROUP BY uc.id, uc.name
#                 ORDER BY uc.name
#             """)
#             result['by_department'] = cursor.fetchall()

#             # 6. Weekly Trend - FULLY FIXED (Critical!)
#             cursor.execute(f"""
#                 SELECT
#                     YEARWEEK(t.date, 1) AS year_week,
#                     CONCAT(
#                         DATE_FORMAT(
#                             MIN(t.date), '%d-%m-%Y'
#                         ),
#                         ' to ',
#                         DATE_FORMAT(
#                             MAX(t.date), '%d-%m-%Y'
#                         )
#                     ) AS week_label,
#                     COALESCE(SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END), 0) AS approved,
#                     COALESCE(SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END), 0) AS rejected,
#                     COALESCE(SUM(CASE WHEN tv.status = 2 THEN 1 ELSE 0 END), 0) AS pending,
#                     COALESCE(SUM(CASE WHEN tv.status = 99 THEN 1 ELSE 0 END), 0) AS on_hold,
#                     COALESCE(SUM(CASE WHEN tv.status = 98 THEN 1 ELSE 0 END), 0) AS sla_breached
#                 FROM glpi_tickets t
#                 LEFT JOIN glpi_ticketvalidations tv ON t.id = tv.tickets_id
#                 WHERE t.is_deleted = 0 
#                   AND t.date {date_range}
#                 GROUP BY YEARWEEK(t.date, 1)
#                 ORDER BY year_week
#             """)
#             result['weekly_trend'] = cursor.fetchall()

#             # 7. Funnel Data - Fixed
#             cursor.execute(f"""
#                 SELECT
#                     COUNT(DISTINCT t.id) AS total_tickets,
#                     COALESCE(SUM(CASE WHEN tv.status = 2 AND t.status != 6 THEN 1 ELSE 0 END), 0) AS under_review,
#                     COALESCE(SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END), 0) AS approved,
#                     COALESCE(SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END), 0) AS rejected
#                 FROM glpi_tickets t
#                 LEFT JOIN glpi_ticketvalidations tv ON t.id = tv.tickets_id
#                 WHERE t.is_deleted = 0 
#                   AND t.date {date_range}
#             """)
#             funnel = cursor.fetchone()
#             result['funnel'] = {
#                 "total_tickets": int(funnel['total_tickets']),
#                 "under_review": int(funnel['under_review']),
#                 "approved": int(funnel['approved']),
#                 "rejected": int(funnel['rejected'])
#             }

#             return JsonResponse({
#                 "success": True,
#                 "date_range": {"from": date1, "to": date2},
#                 "data": result
#             })

#         except Exception as e:
#             return JsonResponse({
#                 "success": False,
#                 "error": str(e),
#                 "data": {}
#             }, status=500)

#         finally:
#             if cursor:
#                 cursor.close()
#             if conn:
#                 conn.close()




# views.py
# views.py
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import MySQLdb
from MySQLdb.cursors import DictCursor
from datetime import date

# ================= DATABASE CONNECTION =================
def get_db_connection():
    return MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="Stemz@123",
        db="old_approval_matrix",   # Your correct DB
        charset='utf8mb4',
        use_unicode=True
    )

PRIORITY_MAP = {
    1: "Very Low", 2: "Low", 3: "Medium",
    4: "High", 5: "Very High", 6: "Critical"
}

@method_decorator(csrf_exempt, name='dispatch')
class HODApprovalDashboardAPI(View):
    def get(self, request):
        conn = None
        cursor = None
        try:
            # AUTO GET USER ID — No more "user_id required" error!
            if request.user.is_authenticated:
                hod_user_id = request.user.id
            else:
                # For testing without login
                user_id_param = request.GET.get('user_id')
                hod_user_id = int(user_id_param) if user_id_param else 1

            start_date = request.GET.get('date1', '2024-01-01')
            end_date = request.GET.get('date2', '2025-12-31')

            conn = get_db_connection()
            cursor = conn.cursor(DictCursor)

            # Get all team members under this HOD
            cursor.execute("""
                SELECT id FROM glpi_users
                WHERE usercategories_id = (
                    SELECT usercategories_id FROM glpi_users 
                    WHERE id = %s AND is_hod = 1
                )
            """, (hod_user_id,))
            team_ids = [row['id'] for row in cursor.fetchall()]
            if not team_ids:
                team_ids = [hod_user_id]  # include self

            placeholders = ','.join(['%s'] * len(team_ids))
            date_filter = f"t.date BETWEEN '{start_date} 00:00:00' AND '{end_date} 23:59:59'"

            # Summary
            cursor.execute(f"""
                SELECT
                    COALESCE(SUM(CASE WHEN tv.status = 2 AND t.status != 6 THEN 1 ELSE 0 END), 0) AS pending_count,
                    COALESCE(SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END), 0) AS approved_count,
                    COALESCE(SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END), 0) AS rejected_count,
                    COALESCE(SUM(CASE WHEN tv.status = 99 THEN 1 ELSE 0 END), 0) AS on_hold_count,
                    COALESCE(SUM(CASE WHEN tv.status = 98 THEN 1 ELSE 0 END), 0) AS sla_breached_count,
                    COUNT(DISTINCT t.id) AS total_tickets
                FROM glpi_ticketvalidations tv
                JOIN glpi_tickets t ON tv.tickets_id = t.id
                WHERE t.is_deleted = 0 AND {date_filter}
                  AND tv.users_id_validate IN ({placeholders})
            """, team_ids)
            summary = cursor.fetchone() or {}

            # Average Response Time
            cursor.execute(f"""
                SELECT COALESCE(ROUND(AVG(TIMESTAMPDIFF(HOUR, tv.submission_date, tv.validation_date)) / 24.0, 2), 0) AS average_response_time
                FROM glpi_ticketvalidations tv
                WHERE tv.validation_date IS NOT NULL
                  AND tv.users_id_validate IN ({placeholders})
            """, team_ids)
            avg_row = cursor.fetchone()
            avg_time = float(avg_row['average_response_time']) if avg_row else 0.0

            # Department Breakdown
            cursor.execute(f"""
                SELECT COALESCE(uc.name, 'Unknown') AS dept_name,
                    COALESCE(SUM(CASE WHEN tv.status = 2 AND t.status != 6 THEN 1 ELSE 0 END), 0) AS pending,
                    COALESCE(SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END), 0) AS approved,
                    COALESCE(SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END), 0) AS rejected,
                    COALESCE(SUM(CASE WHEN tv.status = 99 THEN 1 ELSE 0 END), 0) AS on_hold,
                    COALESCE(SUM(CASE WHEN tv.status = 98 THEN 1 ELSE 0 END), 0) AS sla_breached,
                    COUNT(tv.id) AS total
                FROM glpi_tickets t
                LEFT JOIN glpi_ticketvalidations tv ON t.id = tv.tickets_id AND tv.users_id_validate IN ({placeholders})
                LEFT JOIN glpi_users req ON req.id = t.users_id_recipient
                LEFT JOIN glpi_usercategories uc ON uc.id = req.usercategories_id
                WHERE t.is_deleted = 0 AND {date_filter}
                GROUP BY uc.name
            """, team_ids)
            department_breakdown = {
                (row['dept_name'] or "Unknown"): {
                    "pending": int(row['pending']),
                    "approved": int(row['approved']),
                    "rejected": int(row['rejected']),
                    "on_hold": int(row['on_hold']),
                    "overdue": 0,
                    "sla_breached": int(row['sla_breached']),
                    "total": int(row['total'])
                }
                for row in cursor.fetchall()
            }

            # Priority Breakdown
            cursor.execute(f"""
                SELECT t.priority,
                    COALESCE(SUM(CASE WHEN tv.status = 2 AND t.status != 6 THEN 1 ELSE 0 END), 0) AS pending,
                    COALESCE(SUM(CASE WHEN tv.status = 3 THEN 1 ELSE 0 END), 0) AS approved,
                    COALESCE(SUM(CASE WHEN tv.status = 4 THEN 1 ELSE 0 END), 0) AS rejected,
                    COALESCE(SUM(CASE WHEN tv.status = 99 THEN 1 ELSE 0 END), 0) AS on_hold,
                    COALESCE(SUM(CASE WHEN tv.status = 98 THEN 1 ELSE 0 END), 0) AS sla_breached,
                    COUNT(tv.id) AS total
                FROM glpi_tickets t
                LEFT JOIN glpi_ticketvalidations tv ON t.id = tv.tickets_id AND tv.users_id_validate IN ({placeholders})
                WHERE t.is_deleted = 0 AND {date_filter}
                GROUP BY t.priority
            """, team_ids)
            priority_breakdown = {
                PRIORITY_MAP.get(row['priority'], "Unknown"): {
                    "pending": int(row['pending']),
                    "approved": int(row['approved']),
                    "rejected": int(row['rejected']),
                    "on_hold": int(row['on_hold']),
                    "overdue": 0,
                    "sla_breached": int(row['sla_breached']),
                    "total": int(row['total'])
                }
                for row in cursor.fetchall()
            }

            # User Info
            cursor.execute("SELECT firstname, realname, name FROM glpi_users WHERE id = %s", (hod_user_id,))
            user = cursor.fetchone() or {}

            result = [{
                "id": hod_user_id,
                "name": user.get('name', 'Unknown User'),
                "firstname": user.get('firstname', ''),
                "realname": user.get('realname', ''),
                "email": user.get('name', ''),
                "is_active": True,
                "is_hod": True,
                "department_id": None,
                "department_name": None,
                "location_name": None,
                "locations": None,
                "entities_ids": [],
                "entities_names": [],
                "role_names": [],
                "roles_ids": [],

                "pending_count": int(summary.get('pending_count', 0)),
                "approved_count": int(summary.get('approved_count', 0)),
                "rejected_count": int(summary.get('rejected_count', 0)),
                "on_hold_count": int(summary.get('on_hold_count', 0)),
                "sla_breached_count": int(summary.get('sla_breached_count', 0)),
                "overdue_count": 0,
                "total_tickets": int(summary.get('total_tickets', 0)),

                "average_response_time": avg_time,

                "department_breakdown": department_breakdown,
                "priority_breakdown": priority_breakdown
            }]

            return JsonResponse({
                "success": True,
                "data": result,
                "date_range": {"from": start_date, "to": end_date}
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()