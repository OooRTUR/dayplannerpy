import  sys
import  json
import  pprint
from datetime import  datetime
from datetime import  date
from API.Objects.Task import Task
import  os

# private
DATA_FILE_NAME = os.path.join(os.path.dirname(__file__), 'data.json')



class DayPlanner:


    __data = {
        "Tasks": [],
        "Phones": []
    }

    def __init__(self):
        # self.test_create_tasks()
        self.__initObjectData()
        print("init object data")
        # self.updateJSON()
        # self.shell_main_menu()

    def __initObjectData(self):
        nonobjectdata = self.readJSON()
        tasks = []
        for task in nonobjectdata["Tasks"]:
            tasks.append(Task.decodeJSON(task))
        self.__data["Tasks"] = tasks


    # tasks functions
    def get_tasks(self):
        return [task.__str__() for task in self.__data["Tasks"]]
    def get_tasks_filtered_by_date(self, date):
        return list(filter((lambda x: x.datetime.date() == date),self.__data["Tasks"]))
    def add_new_task(self,dict):
        self.__data["Tasks"].append(Task.decodeJSON(dict))
        self.updateJSON()

    def find_task_by_name(self, searchvalue:str) -> []:
        searchfunc = lambda x: x.name.find(searchvalue) != -1
        return list(filter(searchfunc, self.__data["Tasks"]))

    def delete_task(self, foundtask: Task):
        self.__data["Tasks"].remove(foundtask)
        self.updateJSON()


    def out_phones(self):
        print(*self.phones, sep='\n')


    # work with JSON
    def readJSON(self):
        with open(DATA_FILE_NAME, "r") as read_file:
            return json.load(read_file)
    def updateJSON(self):
        jsondata = {
            "Tasks" : [task.encodeJSON() for task in self.__data["Tasks"]],
            "Phones" : []
        }
        with open(DATA_FILE_NAME, "w") as write_file:
            json.dump(jsondata, write_file, indent=4)



    def test_create_new_task(self, name, done, date):
        self.__data["Tasks"].append(Task(name, done, date))
        self.updateJSON()

    def test_craete_new_phone(self):
        pass

    def test_create_tasks(self):
        t1 = Task("Buy clothes", True, datetime.now())
        t2 = Task("Update pip packages", False, datetime.now())
        self.__data["Tasks"].append(t1)
        self.__data["Tasks"].append(t2)
        self.updateJSON()
