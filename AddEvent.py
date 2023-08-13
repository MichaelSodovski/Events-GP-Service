import arcpy, traceback
from datetime import datetime
from decimal import Decimal
# ---------------------------------------------------------------------------
tbxPath = r"C:\\arcgisserver\\directories\\arcgissystem\\arcgisinput\\AddEventGpS.GPServer\\extracted\\v101\\IRail_Toolbox.tbx" 
events_X = r"C:\\sdeconn\\gisdev.sde\\SDE.EVENT_X"
events_L = r"C:\\sdeconn\\gisdev.sde\\SDE.EVENT_L"
rout = r"C:\\sdeconn\\gisdev.sde\\SDE.ROUTE_L"
fls = r"C:\\sdeconn\\gisdev.sde\\SDE.RAIL_FL_L"
objsp = r"C:\\sdeconn\\gisdev.sde\\OBJ_SAP_P"
# Load required toolboxes
arcpy.ImportToolbox(tbxPath)
# Script arguments
params_input = arcpy.GetParameterAsText(0)  # table to store temp layers
qnum = arcpy.GetParameterAsText(1)
qmart = arcpy.GetParameterAsText(2)
status = arcpy.GetParameterAsText(3)
mahut_code = arcpy.GetParameterAsText(4)
mahut_txt = arcpy.GetParameterAsText(5)
start_date = arcpy.GetParameterAsText(6)
start_time = arcpy.GetParameterAsText(7)
end_date = arcpy.GetParameterAsText(8)
end_time = arcpy.GetParameterAsText(9)
zqnum = arcpy.GetParameterAsText(10)
qmtxt = arcpy.GetParameterAsText(11)
ikun = arcpy.GetParameterAsText(12)
zlong = arcpy.GetParameterAsText(13)
lat = arcpy.GetParameterAsText(14)
tplnr = arcpy.GetParameterAsText(15)
zzkm_num = arcpy.GetParameterAsText(16)
zztokm_num = arcpy.GetParameterAsText(17)
ikunx = lat
ikuny = zlong
operation_type = arcpy.GetParameter(20)
if params_input == '#' or not params_input:
    params_input = r"C:\\arcgisserver\\directories\\arcgissystem\\arcgisinput\\AddEventGpS.GPServer\\extracted\\v101\\temp.gdb\\params_input"  # provide a default value if unspecified

# Local variables:
params_query_table = "QueryTable"
x = datetime.now()
request_id = x.strftime("%d/%m/%Y_%H:%M:%S")  # Calculate request id
rout_result_events = "QueryTableResultEvents1"
ERROR = False

# Helper functions
# ---------------------------------------------------------------------------
def handle_exception(ex):
    arcpy.AddError("An error of type {} occurred. Arguments:\n{}".format(type(ex).__name__, str(ex.args)))
    arcpy.AddError("Here is the full traceback: {}".format(traceback.format_exc()))
    if hasattr(ex, '__context__') and ex.__context__ is not None:
        arcpy.AddError("The previous exception was: {}".format(str(ex.__context__)))
        if hasattr(ex.__context__, '__traceback__'):
            exc_type = type(ex.__context__)
            exc_value = ex.__context__
            exc_traceback = ex.__context__.__traceback__
            traceback_string = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            message = "Here is the traceback for the previous exception: {}".format(traceback_string)
            arcpy.AddError(message)


def delete_existing_event(item_id, layer):
    # Select Layer By Attribute
    query = "{} = '{}'".format("QMNUM", item_id)
    arcpy.AddMessage("Delete existing event " + query)
    try:
        with arcpy.da.UpdateCursor(layer, ['QMNUM'], query) as cursor:
            for row in cursor:
                cursor.deleteRow()
                arcpy.AddMessage("Done delete existing event")
    except Exception as Ex:
        handle_exception(Ex)


def get_polyline_shape(rout_result_events):
    polyline_shape = None
    # Check if the layer has any features
    feature_count = arcpy.GetCount_management(rout_result_events)[0]
    arcpy.AddMessage("Feature count: " + feature_count)
    if int(feature_count) > 0:
        try:
            with arcpy.da.SearchCursor(rout_result_events, ["SHAPE@", "SHAPE@LENGTH"]) as search_cursor:
                for row in search_cursor:
                    polyline_shape = row[0]
                    arcpy.AddMessage("Polyline length: " + str(row[0].length))
                    break
        except Exception as Ex:
            handle_exception(Ex)
    else:
        arcpy.AddMessage("The QueryTableResultEvents1 dataset is empty.")
    return polyline_shape


def get_branch(tplnr):
    query = "{} = '{}'".format("SAP_FL_TRA", tplnr)
    arcpy.AddMessage("" + query)
    arcpy.AddMessage("" + fls)
    arcpy.AddMessage("Searching for branch num...")
    branch_no = ''
    row = None
    try:
        with arcpy.da.SearchCursor(fls, ['BRANCHNO'], query) as cursor:
            for row in cursor:
                arcpy.AddMessage(row[0])
                branch_no = str(row[0]) # the branch number is the same for all the tplnr entries in the rail fl l layer so we address the first one we encounter. 
                break
            else:
                arcpy.AddMessage("ERROR: TPLNR " + tplnr + " not found in layer. can't create event.")
    except Exception as Ex:
         handle_exception(Ex)

    if row is not None:
        del row

    arcpy.AddMessage("found branch number: " + branch_no)
    return branch_no


def get_point_shape(rout_result_events):
    point_shape = None
    arcpy.AddMessage("Getting point shape")
    # Check if the layer has any features
    feature_count = arcpy.GetCount_management(rout_result_events)[0]
    arcpy.AddMessage("Feature count: " + feature_count)
    if int(feature_count) > 0:
        try:
            with arcpy.da.SearchCursor(rout_result_events, ["SHAPE@"]) as search_cursor:
                for row in search_cursor:
                    point_shape = row[0]
                    break
        except Exception as Ex:
            handle_exception(Ex)
    else:
        arcpy.AddMessage("The QueryTableResultEvents1 dataset is empty.")

    return point_shape


def evtLayerHandler(layer, fields):
    try:
        # create a table view.
        arcpy.MakeQueryTable_management(params_input, params_query_table, "USE_KEY_FIELDS", "", "", "requestId = '" + request_id + "'")
        # Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script.
        arcpy.MakeRouteEventLayer_lr(rout, 'BRANCHNO', params_query_table, fields, rout_result_events, "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
        # append dataset to the events_L layer, map the fields from the input to the target/ (without checking for matching schemas)
        arcpy.Append_management(inputs=rout_result_events, target=layer, schema_type="NO_TEST", field_mapping='QMNUM "מספר אירוע" true false true 12 Text 0 0 ,First,#,' + rout_result_events + ',QMNUM,-1,-1;QMART "סוג אירוע" true false true 2 Text 0 0 ,First,#;STATUS "סטאטוס אירוע" true false true 1 Text 0 0 ,First,#;MAHUT_CODE "קוד מהות" true false false 4 Text 0 0 ,First,#;MAHUT_TXT "תיאור מהות" true true false 40 Text 0 0 ,First,#;START_DATE "תאריך תחילת אירוע" true true false 8 Text 0 0 ,First,#;START_TIME "שעת תחילת אירוע" true true false 6 Text 0 0 ,First,#;END_DATE "תאריך סיום אירוע" true true false 8 Text 0 0 ,First,#;END_TIME "שעת סיום אירוע" true true false 6 Text 0 0 ,First,#;ZQMNUM "אירוע אב" true true false 12 Text 0 0 ,First,#;QMTXT "טקסט קצר" true true false 40 Text 0 0 ,First,#;IKUN "איכון" true true false 1 Text 0 0 ,First,#;ZLONG "אורך" true true false 18 Text 0 0 ,First,#;LAT "רוחב" true true false 18 Text 0 0 ,First,#;TPLNR "מיקום פונקציונאלי" true true false 30 Text 0 0 ,First,#,' + rout_result_events + ',TPLNR,-1,-1;ZZKM_NUM "קמ מסילה" true true false 12 Text 0 0 ,First,#;ZZTOKM_NUM "עד קמ מסילה" true true false 12 Text 0 0 ,First,#;MAAGAN_ID "MAAGAN_ID" true true false 4 Long 0 10 ,First,#;SHAPE.LEN "SHAPE.LEN" false false true 0 Double 0 0 ,First,#', subtype="")
    except Exception as Ex:
            handle_exception(Ex)


def update_event_handler(layer, shape):
    delete_existing_event(qnum, layer)
    if layer == events_L:
        fields = ['QMNUM','TPLNR','SHAPE@','QMART','MAHUT_CODE','MAHUT_TXT','START_DATE','START_TIME','END_DATE', 'END_TIME','ZQMNUM','QMTXT','IKUN','ZLONG','LAT','ZZKM_NUM','ZZTOKM_NUM','MAAGAN_ID','STATUS']
        row_values = (qnum, tplnr, shape, qmart, mahut_code, mahut_txt, start_date, start_time, end_date, end_time, zqnum, qmtxt, ikun,zlong, lat, zzkm_num, zztokm_num, qnum, status)
    elif layer == events_X:
        fields = ['QMNUM', 'QMART', 'MAHUT_CODE', 'MAHUT_TXT', 'START_DATE', 'START_TIME', 'END_DATE', 'END_TIME','ZQMNUM', 'QMTXT', 'IKUN', 'ZLONG', 'LAT', 'TPLNR', 'ZZKM_NUM', 'ZZTOKM_NUM','SHAPE@XY','MAAGAN_ID','STATUS']
        row_values = (qnum, qmart, mahut_code, mahut_txt, start_date, start_time, end_date, end_time, zqnum, qmtxt,ikun, zlong, lat, tplnr, zzkm_num, zztokm_num, shape, qnum, status)
    
    try:
        max_id = max(r[0] for r in arcpy.da.SearchCursor(layer, 'OBJECTID'))
        arcpy.AddMessage("MAX INDEX IN THE TABLE: " + str(max_id))
        with arcpy.da.UpdateCursor(layer, fields, where_clause="OBJECTID={}".format(max_id)) as cursor:
            for row in cursor:
                cursor.updateRow(row_values)
                message = "Inserted new event to {}".format(layer)
                arcpy.AddMessage(message)
    except Exception as Ex:
        handle_exception(Ex)

#Main actions
# ---------------------------------------------------------------------------
def create_new_xy_event(x, y):
    arcpy.AddMessage("Inserting new point event at point " + str(x) + "," + str(y))
    fields = ['QMNUM', 'QMART', 'MAHUT_CODE', 'MAHUT_TXT', 'START_DATE', 'START_TIME', 'END_DATE', 
    'END_TIME', 'ZQMNUM', 'QMTXT', 'IKUN', 'ZLONG', 'LAT', 'TPLNR', 'ZZKM_NUM', 'ZZTOKM_NUM', 'SHAPE@XY', 'MAAGAN_ID', 'STATUS']
    # handle delete an existing event with the current id prior to adding the new one. 
    delete_existing_event(qnum, events_X)
    try:
        with arcpy.da.InsertCursor(events_X, fields) as cursor:
            row_values = (qnum, qmart, mahut_code, mahut_txt, start_date, start_time, end_date, 
            end_time, zqnum, qmtxt, ikun, float(y), float(x), tplnr, zzkm_num, zztokm_num, (float(x), float(y)), qnum, status)
            cursor.insertRow(row_values)
            arcpy.AddMessage("Inserted new point to events_X")
    except Exception as Ex:
        handle_exception(Ex)


def create_new_line_event(tplnr, km_from, km_to):
    arcpy.AddMessage("Inserting new line event, tplnr : " + tplnr + ", km_from : " + km_from + ", km_to : " + km_to)
    global ERROR
        
    if tplnr == '#' or not tplnr:
        arcpy.AddMessage("ERROR: no TPLNR could not find functional location in layer. Can't create event")
        ERROR = True
        return	

    branch_no = get_branch(tplnr)
    arcpy.AddMessage("BRANCH: " + str(branch_no))
    if branch_no == None or " ":
        arcpy.AddMessage("ERROR: Failed to get branch.")
        ERROR = True
        return 

    try:
        with arcpy.da.InsertCursor(params_input, ["QNUM", "KM", "TOKM", "BRANCHNO", "requestId"]) as cursor:
            cursor.insertRow((qnum, zzkm_num, zztokm_num, branch_no, request_id))
    except Exception as Ex:
        handle_exception(Ex)

    evtLayerHandler(events_L, "BRANCHNO LINE KM TOKM")

    polyline_shape = get_polyline_shape(rout_result_events)
    if not polyline_shape:
        arcpy.AddMessage("ERROR: Failed to create polyline shape.")
        ERROR = True
        return

    update_event_handler(events_L, polyline_shape)
   

def add_event_fom_fl_center(tplnr):
	global ERROR
	arcpy.AddMessage("Inserting new point event from tplnr : " + tplnr)
	if tplnr == '#' or tplnr == '':
		arcpy.AddMessage("ERROR: The provided TPLNR is not valid.")
		ERROR = True
		return
		
	arcpy.AddMessage("TPLNR is valid: " + tplnr)
	if params_input == '#' or params_input == '' or params_input == None:
		arcpy.AddMessage("ERROR: The provided params input table is not found. check the directory.")
		ERROR = True
		return
	
	else:
		query = "{} = '{}'".format("OBJECT_NO", tplnr)
		arcpy.AddMessage("Select FL " + query)
		try:
			row_proccessed = False # flag to track if any of the rows were proccessed.
			with arcpy.da.SearchCursor(objsp, ['SHAPE@'], query) as cursor: 
				for row in cursor:
						row_proccessed = True
						fl_geom = row[0]
						arcpy.AddMessage("GEOM CENTROID: " + str(fl_geom.centroid))
						if fl_geom is not None:
							centroid = fl_geom.centroid
							arcpy.AddMessage("Mid point of fl is: " + str(centroid.X) + "," + str(centroid.Y))
							create_new_xy_event(centroid.X, centroid.Y)
							break
			if not row_proccessed:
				arcpy.AddMessage("ERROR: Script FAILED - no shape was retrieved with the provided TPLNR.")
		except Exception as Ex:
			handle_exception(Ex)


def add_event_from_rout_point(tplnr, km):
    arcpy.AddMessage("Inserting new point event from rout , tplnr : " + tplnr + ", km : " + km )
    global ERROR

    if tplnr == '#' or tplnr == '' or not params_input:
        arcpy.AddMessage("ERROR: no TPLNR could not find functional location in layer. Cant create event")
        ERROR = True
        return
    
    branch_no = get_branch(tplnr)
    if branch_no == None:
        return

    arcpy.AddMessage("km " + km + ' at ' + branch_no)
    # insert to temp table in order to create route event
    if branch_no != '':
        try:
            arcpy.AddMessage('Adding row to temp table...')
            with arcpy.da.InsertCursor(params_input, ["QNUM", "KM", "TOKM", "BRANCHNO", "requestId"]) as cursor:
                cursor.insertRow((qnum, zzkm_num, zztokm_num, branch_no, request_id))
        except Exception as Ex:
            handle_exception(Ex)

        evtLayerHandler(events_X, "BRANCHNO POINT KM")

        point_shape = get_point_shape(rout_result_events)
        if not point_shape:
            arcpy.AddMessage("ERROR: Failed to create point shape.")
            ERROR = True
            return

        update_event_handler(events_X, point_shape)


# Main
# ---------------------------------------------------------------------------
arcpy.AddMessage("processing request " + request_id)

try:
    if operation_type == 1:
        arcpy.AddMessage("FL center - point")
        add_event_fom_fl_center(tplnr)
    elif operation_type == 2:
        arcpy.AddMessage("FL rout km - point")
        add_event_from_rout_point(tplnr, zzkm_num)
    elif operation_type == 3:
        arcpy.AddMessage("FL rout kmf kmt - line")
        create_new_line_event(tplnr, zzkm_num, zztokm_num)
    elif operation_type == 4:
        arcpy.AddMessage("x y - point")
        create_new_xy_event(ikunx, ikuny)
    elif operation_type == "":
        arcpy.AddMessage("unsupported operation type")
    else:
        arcpy.AddMessage("OK")
except Exception as Ex:
      ERROR = True
      arcpy.AddMessage("ERROR. Failed adding event.")
      handle_exception(Ex)


