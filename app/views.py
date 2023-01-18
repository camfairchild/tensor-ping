# This file defines the routes for tensor-ping.
# Copyright (C) 2022-2023 Cameron Fairchild 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from app import app
from flask import render_template, request
import bittensor
from enum import Enum

MAX_FAUCET_OUT: float = 1024.0
subtensor_url = "<chain_endpoint>:9944"

class ReturnCode(Enum):
	NoReturn = 0; # Default Value
	Success = 1; # Succesfull query.
	Timeout = 2; # Request timeout.
	Backoff = 3; # Call triggered a backoff.
	Unavailable = 4; # Endpoint not available.
	NotImplemented = 5; # Modality not implemented.
	EmptyRequest = 6; # Request is empty.
	EmptyResponse = 7; # Response is empty.
	InvalidResponse = 8; # Request is invalid.
	InvalidRequest = 9; # Response is invalid.
	RequestShapeException = 10; # Request has invalid shape.
	ResponseShapeException = 11; # Response has invalid shape.
	RequestSerializationException = 12; # Request failed to serialize.
	ResponseSerializationException = 13; # Response failed to serialize.
	RequestDeserializationException = 14; # Request failed to deserialize.
	ResponseDeserializationException = 15; # Response failed to deserialize.
	NotServingNucleus = 16; # Receiving Neuron is not serving a Nucleus to query.
	NucleusTimeout = 17; # Processing on the server side timeout.
	NucleusFull = 18; # Returned when the processing queue on the server is full.
	RequestIncompatibleVersion = 19; # The request handler is incompatible with the request version.
	ResponseIncompatibleVersion = 20; # The request handler is incompatible with the request version.
	SenderUnknown = 21; # The requester is not known by the reciever. 
	UnknownException = 22; # Unknown exception.
	Unauthenticated = 23; # Authentication failed.
	BadEndpoint = 24; # Dummy endpoint

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/ping', methods=['GET'])
def ping():
    UID = int(request.args.get('uid').strip())
    subtensor = bittensor.subtensor(
        network="endpoint",
        chain_endpoint=subtensor_url
    )
    forward_text = request.args.get('forward_text')
    wallet = bittensor.wallet()    
    wallet.regenerate_hotkey(mnemonic="<validator_mnemonic>", use_password=False, overwrite=True)

    dend = bittensor.dendrite( wallet = wallet )
    neuron = subtensor.neuron_for_uid( UID )
    endpoint = bittensor.endpoint.from_neuron( neuron )

    # === Query the eoints ===
    # Makes the dendrite call into the network returning the representations
    # for each of the endpoints. The return ops can be used to filter weights and outputs.
    # query_responses: (List[torch.float64]): responses from each endpoint.
    # query_responses.shape = self.config.nucleus.topk * num_synapses * [batch_size, sequence_len, synapse_dim]
    # return_ops: (torch.int64): Return ops.
    # return_ops.shape = self.config.nucleus.topk * [num_synapses]
    response_codes, time, query_responses = dend.generate(endpoint, forward_text, num_to_generate=64)

    t = time[0]
    response_text = response_codes[0]
    response_code = ReturnCode[response_text]
    response = {
        "uid": UID,
        "ip": endpoint.ip,
        "port": endpoint.port,
        "response_code": response_code,
        "response_time": float(t),
        "forward_text": forward_text,
        "response_text": query_responses,
        "stake": bittensor.Balance.from_tao(neuron.stake).tao
    }

    if response_code == ReturnCode.Success:
       return response, 200
    else:
        return response, 400

@app.route('/balance', methods=['GET'])
def balance():
    addr = request.args.get('addr')
    if (addr is None):
        return "Missing address", 400

    subtensor = bittensor.subtensor(
        network="endpoint",
        chain_endpoint=subtensor_url,
    )

    with subtensor.substrate as substrate:
        if (not substrate.is_valid_ss58_address(addr)):
            return "Invalid address", 400
        
    bal: bittensor.Balance = subtensor.get_balance(addr)
    return {
        "addr": addr,
        "balance": bal.tao,
    }

@app.route('/faucet', methods=['GET'])
def faucet():
    addr = request.args.get('addr')
    if (addr is None):
        return "Missing address", 400
    
    subtensor_nobu = bittensor.subtensor(
        network="nobunaga",
    )

    with subtensor_nobu.substrate as substrate:
        if (not substrate.is_valid_ss58_address(addr)):
            return "Invalid address", 400
        
    bal: bittensor.Balance = subtensor_nobu.get_balance(addr)
    to_give = bal.tao - MAX_FAUCET_OUT
    if to_give > 0:
        # give test tao
        wallet = bittensor.wallet(name="testnet_wallet")    
        wallet.regenerate_coldkey(seed="<faucet_seed>", use_password=False, overwrite=True)

        sent: bool = wallet.transfer(subtensor=subtensor_nobu, dest=addr, amount=bittensor.Balance.from_tao(to_give), wait_for_finalization=True)

        if not sent:
            return "Error sending Test TAO", 500

        return "Sent!", 200
    else:
        return f"You already have {MAX_FAUCET_OUT:0.2f} Test TAO", 400

