import "./token_wallet";
import "./messages";
import "@stdlib/ownable";
import "@stdlib/deploy";
import "@"
// const jetton_master: Address = address("0:5085f3c1a165a64ae5947d5cd7aab9871c369149bbc036a89e8f830dd0b9c116");
// CONSTANTS

const mitTons: Int = ton("0.01");
const forwardTonAmount: Int = 1;
const notificationAmount: Int = 1;
const tracking_address: Address = address("UQBVxO80__1rBGqrWzJjbMf5ZLmk0zyh3cps4vhl8Itwbjl1");
// const TheOpenTimeAddress: Address = address("UQBVxO80__1rBGqrWzJjbMf5ZLmk0zyh3cps4vhl8Itwbjl1");
const TheOpenTimeAddress: Address = address("EQBGhqLAZseEqRXz4ByFPTGV7SVMlI4hrbs-Sps_Xzx01x8G");

// statuses
const OfferCreated: Int = 0;
const OfferPublished: Int = 1;
const OfferAccepted: Int = 2;
const OfferCompleted: Int = 3;
const OfferConfirmed: Int = 4;
const OfferAppelation: Int = 5;
const OfferClosed: Int = 6;


const job_posted: Int = 1;

message Approve {
    amount: Int as coins;
}

message ChangeStatus {
    status: Int as uint32;
}

struct JobOfferCloseState {
    doer: Bool;
    owner: Bool;
}

struct ContractData {
    title: String;
    description: String;
    price: Int as uint64;
    owner: Address;
    doer: Address?;
    is_locked: Bool;
    state: Int as uint32;
    jetton_master: Address;
    balance: Int as coins;
    my_jetton_address: Address;
}

contract JobOffer with Deployable{

    order: String;
    title: String;
    description: String;
    price: Int as coins;
    owner: Address;
    doer: Address?;
    job_state: JobOfferCloseState;
    state: Int;
    is_locked: Bool = false;
    jetton_master: Address;

    init(title: String, description: String, price: Int, order: String, jetton_master: Address) {
        self.order = order;
        self.title = title;
        self.description = description;
        self.price = price;
        self.jetton_master = jetton_master;
        self.owner = sender();
        self.job_state = JobOfferCloseState{doer: false, owner: false};
        self.state = OfferCreated;
    }

    receive("get_job") {
        require(!self.is_locked, "Job already got");
        require(sender() != self.owner, "Poster could not pick up job");
        let doer_address: Address = sender();
        self.doer = sender();
        self.is_locked = true;
    }

    

    receive(msg: ChangeStatus) {
        return ;
    }

    receive("Deploy") {
        let ctx: Context = context();
        // let initJ: StateInit = initOf TokenWallet(myAddress(), self.jetton_master);
        self.is_locked = false;
        
        send(SendParameters {
                to: tracking_address,
                value: ctx.value / 2,
                mode: SendIgnoreErrors,
                bounce: false,
                body: self.order.asComment()
        });
        
        // send(SendParameters {
        //     to: contractAddress(initJ),
        //     value: ctx.value,
        //     mode: SendIgnoreErrors,
        //     bounce: false,
        //     body: "Deploy".asComment()
        // });
    }

    receive("close_offer") {
        // check job offer state
    }

    receive(msg: Approve) {
        require(sender() == TheOpenTimeAddress, "Only platform method");
        require(self.price == msg.amount, "Price and deposit did not equal");
        self.state = OfferPublished;
    }

    receive("revoke") {
        require(self.owner == sender(), "Offer could be revoked only by owner.");
        require(self.state == OfferPublished, "Could not on this stage. ");
        self.send_deposit(self.owner, self.price);
        self.state = OfferClosed;
    }

    fun send_deposit(address: Address, amount: Int) {
        // let my_wallet: StateInit = ini
        let init: StateInit = initOf TokenWallet(myAddress(), self.jetton_master);  
        let my_jetton_address: Address = contractAddress(init);
        let forward_destination: Int = ton("0.91");
        send(SendParameters{
            to: my_jetton_address, 
            value: forward_destination,
            mode: SendRemainingValue, 
            bounce: false,
            body: Transfer{ // 0x0f817ea5
                query_id: 0,
                amount: amount,
                destination: address,
                response_destination: address,
                custom_payload: beginCell().endCell(),
                forward_ton_amount: forward_destination,
                forward_payload: beginCell().endCell().asSlice(),
            }.toCell(),
            code: init.code,
            data: init.data
        });
    }

    fun change_status(new_status: Int) {
        // logic for changing status
    }

    get fun job_data(): ContractData {
        return ContractData{
            title: self.title,
            description: self.description,
            price: self.price,
            owner: self.owner,
            doer: self.doer,
            is_locked: self.is_locked,
            state: self.state,
            jetton_master: self.jetton_master,
            balance: myBalance(),
            my_jetton_address: self.jetton_wallet()

        };
    }

    get fun jetton_wallet(): Address {
        let init: StateInit = initOf TokenWallet(myAddress(), self.jetton_master);
        let wallet_address: Address = contractAddress(init);
        return wallet_address;
    }

    fun jetton_wallet_address(): Address {
        let init: StateInit = initOf TokenWallet(myAddress(), self.jetton_master);
        let wallet_address: Address = contractAddress(init);
        return wallet_address;
    }

    fun send_notification(message: String, address: Address) {
        send(SendParameters{
                to: tracking_address,
                value: 0,
                mode: SendIgnoreErrors,
                // bounce: false,
                body: message.asComment(),
        });
    }





    
}
