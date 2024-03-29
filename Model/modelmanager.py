from Model.boxm import BoxM
from Model.prisonerm import PrisonerM
from Model.probabilities_handler import ProbabilitiesHandler


class ModelManger:
    """
    A class representing the managing object that is trusted of the backend part of the game.\n
    The class coordinate between the changes that are taking place in the business logic, the object
    is also handle different events that come from the UI and respond according to the event.\n

    Attributes:\n

    dict_rounds: all rounds and its relational list representation -> dictionary of {round number: list of box numbers}.\n
    dict_prisoners: all prisoners mapped by their number-> dictionary of {prisoner number: PrisonerM object}.\n
    dict_boxes:  all boxes mapped by their number-> dictionary of {box number: BoxM object}.\n
    listener: coordinates the activity between the backend and the frontend -> Controller object.\n
    current_round: the number of the current round-> int.\n
    current_prisoner: the current prisoner number-> int.\n
    succeeded: the number of succeeded prisoners in the current game-> int.\n
    num_prisoners: the total number of prisoners -> int.\n
    num_rounds: the total number of rounds -> int.\n
    print_specifically: user choice if he/she wants to print to file "PrisonersResults.txt" the specific route of each prisoner or not -> bool.\n
    prob_handler: a probability handler object, handles with probability calculations of each round and the total success rate -> ProbabilitiesHandler object.
    """

    def __init__(self) -> None:
        """
        Initialize ModelManger Object.\n
        :return: None.
        """
        self.dict_rounds = {}  # dict of {round_num:list dependencies of boxes}
        self.dict_prisoners = {}  # dict of {num_pris:prisoner}
        self.dict_boxes = {}  # dict of {num_box:box}
        self.current_round = 1
        self.current_pris_num = 1
        self.succeeded = 0
        self.total_pris = 0
        self.total_rounds = 1
        self.is_running_game = False
        self.initial_pos = None
        self.prob_handler = None
        self.listener = None

    # ************************* MVC Methods ******************************************#

    def model_request_box(self) -> None:
        """
        Method for requesting from ViewManager a specific box to be placed on screen.\n
        :return: None.
        """
        self.listener.model_need_box(self.dict_prisoners[self.current_pris_num].target_box.box_num)

    def model_request_box_dimensions(self) -> tuple[int, int]:
        """
        Method for requesting from ViewManager box image dimensions in purpose to help the prisoner calculate its route to box without collisions.\n
        :return: a position tuple in form -> tuple[int,int].
        """
        return self.listener.model_need_box_dimensions()

    def model_request_pris_dimensions(self) -> tuple[int, int]:
        """
        Method for requesting from ViewManager prisoner image dimensions in purpose to help the prisoner calculate its route to box without collisions.\n
        :return: a position tuple in form -> tuple[int,int].
        """
        return self.listener.model_need_pris_dimensions()

    def model_request_to_open_box(self, current_box_num) -> None:
        """
        Method for requesting from ViewManager to open specific box number.\n
        :param current_box_num: int, a number that represents specific box number.
        :return: None.
        """
        self.listener.model_need_to_open_box(current_box_num)

    def model_request_success_prisoner(self, current_pris_num, num_succeeded) -> None:
        """
        Method for requesting from ViewManager to open specific box number.\n
        :param current_pris_num: int, a number that represents prisoner number.
        :param num_succeeded: int, a number that represents the number of prisoners that managed to escape.
        :return: None.
        """
        self.listener.model_need_to_report_success(current_pris_num, num_succeeded)

    def model_request_failure_prisoner(self, current_pris_num) -> None:
        """
        Method for requesting from ViewManager to open specific box number.\n
        :param current_pris_num: int, a number that represents prisoner number.
        :return: None.
        """
        self.listener.model_need_to_report_failure(current_pris_num)

    def model_request_time_prisoner(self, time: float) -> None:
        """
        Method for requesting from ViewManager to open specific box number.\n
        :param time: float, a number that represents the time that took the prisoner to get his target box.
        :return: None.
        """
        self.listener.model_need_to_update_time(time)

    def ntfy_to_view_get_all_boxes_pos(self) -> dict:
        """
        Method that fetch all boxes position mapped by their number in purpose to help the prisoner calculate its route.\n
        :return: dict in form ->  dict[int:tuple[int,int]].
        """
        return self.listener.model_need_all_boxes_on_screen_pos()  # will return dict of {num_box:position}

    def set_listener(self, listener) -> None:
        """
        Method that sets Listener to model.\n
        :param listener: Controller, a controller Object.
        :return: None.
        """
        self.listener = listener

    # ********************************************************************************#

    def init_prisoners(self, num_pris: int, initial_pos: tuple) -> None:
        """
        Initialization method for creating new PrisonerM objects according the round boxes dependencies.\n
        :param num_pris: int, the number o prisoners.
        :param initial_pos: tuple, position tuple of (x,y) in form -> tuple[int,int].
        :return: None.
        """
        if self.dict_prisoners:
            self.dict_prisoners = {}
        for index_pris in range(num_pris):
            self.dict_prisoners[index_pris + 1] = PrisonerM(num_prisoner=index_pris + 1,
                                                            position=initial_pos,
                                                            pace=5,
                                                            all_boxes=self.dict_boxes,
                                                            target_box=self.dict_boxes[index_pris + 1],
                                                            all_prisoners=self.total_pris)

    def init_boxes(self, num_pris: int) -> None:
        """
        Initialization method for creating new BoxM objects according the round boxes dependencies and screen placing.\n
        :param num_pris: int, the number of prisoners.
        :return: None.
        """
        if self.dict_boxes:
            self.dict_boxes = {}
        for index_box in range(num_pris):
            box = BoxM(box_num=index_box + 1)
            self.dict_boxes[index_box + 1] = box
        for box_num in self.dict_boxes.keys():  # box num starts from 1 to n+1
            self.dict_boxes[box_num].set_next_box(self.dict_boxes[self.dict_rounds[self.current_round][box_num - 1]])  # redirecting each box to current next box
        self.set_all_boxes_pos()

    def set_all_boxes_pos(self) -> None:
        """
        Set method for all boxes positions on screen, the method sets the positions by the information that the controller hand over from the view.\n
        :return: None.
        """
        boxes_on_screen = self.ntfy_to_view_get_all_boxes_pos()
        for box_num in self.dict_boxes.keys():
            if box_num not in boxes_on_screen.keys():
                continue  # There are might more boxes on screen up ahead
            self.dict_boxes[box_num].set_pos(boxes_on_screen[box_num])

    def setup_game(self, num_pris: int, num_rounds: int, initial_pos: tuple[int, int],
                   print_specifically: bool) -> dict:
        """
        The method that initialize all  calculations by ProbabilitiesHandler and organize all the prisoner and boxes objects.\n
        :param num_pris: int, the total number of prisoners.
        :param num_rounds: int, the total number of rounds.
        :param initial_pos: tuple, the position tuple of (x,y) in form -> tuple[int,int].
        :param print_specifically: bool ,the indication for specification in the PrisonersResults.txt.
        :return: the round dict of list dependencies.
        """
        self.prob_handler = ProbabilitiesHandler(num_prisoners=num_pris, num_rounds=num_rounds,
                                                 print_specifically=print_specifically)
        self.dict_rounds = self.prob_handler.run_probabilities()
        self.current_round = 1
        self.total_rounds = num_rounds
        self.total_pris = num_pris
        self.initial_pos = initial_pos
        self.init_boxes(num_pris=num_pris)
        self.init_prisoners(num_pris=num_pris, initial_pos=initial_pos)
        self.is_running_game = True
        return self.dict_rounds

    def run_game(self) -> None:
        """
        The actual method that responsible for the game functionality, the method is operated by the view run loop which is infinite.\n
        All the prisoners are searching their number by ProbabilityManager calculations.\n
        :return: None.
        """
        status = self.dict_prisoners[self.current_pris_num].is_still_searching()  # status[0] is indication of search, status[1] is the current box num

        self.model_request_time_prisoner(self.dict_prisoners[self.current_pris_num].time_interval)  # Updating the view on time intervals

        if status[1] in self.dict_prisoners[self.current_pris_num].visited_boxes.keys():  # If the prisoner has reached the current target box
            self.model_request_to_open_box(status[1])
        if status[0]:
            if not self.dict_prisoners[self.current_pris_num].on_exit:  # -1 is the exit point
                self.model_request_box()  # Model alerts the View that he needs a new box, the view should bring it to screen if it's not there

            box_dimensions = self.model_request_box_dimensions()  # Getting the dimensions of box image
            pris_dimensions = self.model_request_pris_dimensions()  # Getting the dimensions of box image
            self.dict_prisoners[self.current_pris_num].navigate(box_width=box_dimensions[0],
                                                                box_height=box_dimensions[1],
                                                                pris_width=pris_dimensions[0],
                                                                pris_height=pris_dimensions[1])
        else:

            # Replacing Prisoner
            if self.dict_prisoners[self.current_pris_num].found_number:
                self.succeeded += 1
                self.model_request_success_prisoner(self.current_pris_num, self.succeeded)  # Reporting to view on successes

            # Reporting to view on failures
            else:
                self.model_request_failure_prisoner(self.current_pris_num)
            self.current_pris_num += 1

            # Replacing Round
            if self.current_pris_num > self.total_pris:
                self.current_pris_num = 1
                self.current_round += 1
                self.succeeded = 0

                # In case there are more rounds to go
                if self.current_round <= self.total_rounds:
                    self.init_boxes(num_pris=self.total_pris)
                    self.init_prisoners(num_pris=self.total_pris, initial_pos=self.initial_pos)

                # Intializing parameters of ModelManger
                else:
                    self.stop_game()

    def get_current_pris_num(self) -> int:
        """
        Method for fetching the current prisoner number.\n
        :return: int.
        """
        return self.current_pris_num

    def get_current_pris_pos(self) -> tuple[int, int]:
        """
        Method for fetching the current prisoner position.\n
        :return: a position tuple of (x,y) in form -> tuple[int,int].
        """
        return self.dict_prisoners[self.current_pris_num].get_pos()

    def get_game_status(self) -> bool:
        """
        Method for getting the state of the game.\n
        :return:bool, an indication of game status.
        """
        return self.is_running_game

    def stop_game(self) -> None:
        """
        Method for stop the current game that runs.\n
        :return: None.
        """
        self.is_running_game = False
        self.succeeded = 0
        self.current_round = 1
        self.current_pris_num = 1

    def run_statistics(self, num_prisoners, num_rounds, print_specify):
        """
        Method that tells the probabilities' handler to calculate statistics.\n
        :param num_prisoners: int, the number of prisoners.
        :param num_rounds: int, the number of rounds.
        :param print_specify: bool, indication to print specified results.

        :return: None.
        """
        self.prob_handler = ProbabilitiesHandler(num_prisoners, num_rounds, print_specify)
        self.prob_handler.output = ""
        self.prob_handler.run_probabilities()

    def get_statistics(self) -> str:
        """
        Method that get the statistics data.\n

        :return: None.
        """
        return self.prob_handler.output
