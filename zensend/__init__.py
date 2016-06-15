import requests

class ZenSendException(Exception):
  def __init__(self, http_code, json):
    self.http_code = http_code

    if json is None:
      self.failcode = None
      self.parameter = None
      self.cost_in_pence = None
      self.new_balance_in_pence = None
    else:
      self.failcode = json["failcode"]
      self.parameter = json.get("parameter")
      self.cost_in_pence = json.get("cost_in_pence")
      self.new_balance_in_pence = json.get("new_balance_in_pence")

    message = "http_code: %s failcode: %s parameter: %s" % (self.http_code, self.failcode, self.parameter)
    super(ZenSendException, self).__init__(message)

class SmsResponse:
  numbers = None
  sms_parts = None
  encoding = None
  tx_guid = None
  cost_in_pence = None
  new_balance_in_pence = None

class OperatorLookupResponse:
  mnc = None
  mcc = None
  operator = None
  cost_in_pence = None
  new_balance_in_pence = None

class Client:
  def __init__(self, api_key, url = "https://api.zensend.io", verify_url = "https://verify.zensend.io"):
    self.api_key = api_key
    self.url = url
    self.verify_url = verify_url

  def check_balance(self):
    result = requests.get(self.url + "/v3/checkbalance", headers = {"X-API-KEY": self.api_key})
    json = self.__handle_result(result)
    return json["balance"]

  def lookup_operator(self, msisdn):
    result = requests.get(self.url + "/v3/operator_lookup", params = {"NUMBER": msisdn}, headers = {"X-API-KEY": self.api_key})
    json = self.__handle_result(result)
    response = OperatorLookupResponse()
    response.mnc = json["mnc"]
    response.mcc = json["mcc"]
    response.operator = json["operator"]
    response.cost_in_pence = json["cost_in_pence"]
    response.new_balance_in_pence = json["new_balance_in_pence"]
    return response

  def get_prices(self):
    result = requests.get(self.url + "/v3/prices", headers = {"X-API-KEY": self.api_key})
    json = self.__handle_result(result)
    return json["prices_in_pence"]

  def create_msisdn_verification(self, number, message = None, originator = None):
    params = {"NUMBER": number}

    if message is not None:
      params["MESSAGE"] = message
    if originator is not None:
      params["ORIGINATOR"] = originator

    result = requests.post(self.verify_url + "/api/msisdn_verify", params, headers = {"X-API-KEY": self.api_key})

    json = self.__handle_result(result)

    return json["session"]

  def msisdn_verification_status(self, session):
    result = requests.get(self.verify_url + "/api/msisdn_verify", params = {"SESSION": session}, headers = {"X-API-KEY": self.api_key})
    json = self.__handle_result(result)
    return json["msisdn"]

  def send_sms(self, body, originator, numbers, timetolive_in_minutes = None, originator_type = None, encoding = None):
    params = {"BODY": body, "ORIGINATOR": originator, "NUMBERS": ",".join(self.__no_commas(numbers))}
    if timetolive_in_minutes is not None:
      params["TIMETOLIVE"] = timetolive_in_minutes
    if originator_type is not None:
      params["ORIGINATOR_TYPE"] = originator_type
    if encoding is not None:
      params["ENCODING"] = encoding

    result = requests.post(self.url + "/v3/sendsms", params, headers = {"X-API-KEY": self.api_key})
    json = self.__handle_result(result)
    response = SmsResponse()
    response.sms_parts = json["smsparts"]
    response.encoding = json["encoding"]
    response.numbers = json["numbers"]
    response.tx_guid = json["txguid"]
    response.cost_in_pence = json["cost_in_pence"]
    response.new_balance_in_pence = json["new_balance_in_pence"]
    return response

  def __handle_result(self, result):
    content_type = result.headers['content-type']
    if content_type is not None and "application/json" in content_type:
      json = result.json()
      if "success" in json:
        return json["success"]
      elif "failure" in json:
        failure = json["failure"]
        raise ZenSendException(result.status_code, failure)
      else:
        raise ZenSendException(result.status_code, None)
    else:
      raise ZenSendException(result.status_code, None)

  def __no_commas(self, numbers):
    for number in numbers:
      if "," in number:
        raise ValueError("',' not allowed in numbers")
    return numbers
